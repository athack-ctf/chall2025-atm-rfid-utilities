from smartcard.System import readers
from smartcard.util import toHexString, toASCIIString
from smartcard.CardConnection import CardConnection
import time
import smartcard


KEY_A = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
KEY_NUMBER = 0x00

class WrongKeyException(Exception):
    pass

def load_keyA(connection):
    """Load a key into ACR122U's key storage"""
    load_key_apdu = [0xFF, 0x82, 0x00, KEY_NUMBER, 0x06] + KEY_A
    response, sw1, sw2 = connection.transmit(load_key_apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        return True
    else:
        # print(f"Loading key failed. SW1: {sw1}, SW2: {sw2}")
        return False


def authenticate_with_keyA(connection, sector):
    """Authenticate using Key A on a specific sector."""
    block = sector * 4 # last block of sector
    command = [0xFF, 0x86, 0x00, KEY_NUMBER, 0x05, 0x01, 0x00, block, 0x60, 0x00]
    response, sw1, sw2 = connection.transmit(command)
    if sw1 == 0x90 and sw2 == 0x00:
        # print(f"Authentication Success sector {sector}")
        return True
    else:
        # print(f"Authentication failed. SW1: {sw1}, SW2: {sw2}")
        raise WrongKeyException



def read_block(connection, sector, block):
    """Read 16 bytes from a specific block in a sector using Key A."""
    if not authenticate_with_keyA(connection, sector):
        return None

    # Command to read a specific block (usually 4-byte blocks)
    command = [0xFF, 0xB0, 0x00, block, 0x10]  # 0x10 is for reading 16 bytes
    response, sw1, sw2 = connection.transmit(command)
    
    if sw1 == 0x90 and sw2 == 0x00:
        return response
    else:
        # print(f"Failed to read block {block}. SW1: {sw1}, SW2: {sw2}")
        return None


def write_block(connection, sector, block, data):
    """Write 16 bytes of data to a specific block in a sector."""
    if not authenticate_with_keyA(connection, sector):
        return False

    if (block % 4) == 3:
        # print("CAREFUL: overwriting key/ACL block?")
        return False
    
    # Check if data is 16 bytes long
    if len(data) != 16:
        # print("Data must be exactly 16 bytes long.")
        return False
    
    # Command to write data to the block
    command = [0xFF, 0xD6, 0x00, block, 0x10] + data
    response, sw1, sw2 = connection.transmit(command)
    
    if sw1 == 0x90 and sw2 == 0x00:
        return True
    else:
        print(f"Failed to write block {block}. SW1: {sw1}, SW2: {sw2}")
        return False

def read_uid(connection):
    # Read UID (Block 0)
    apdu_read_uid = [0xFF, 0xCA, 0x00, 0x00, 0x04]
    response, sw1, sw2 = connection.transmit(apdu_read_uid)
    if sw1 == 0x90 and sw2 == 0x00:
        return response
    else:
        print(f"Failed to read UID. SW1: {sw1}, SW2: {sw2}")
        return False




def read_first_name_from_card(c):
    first_name_data = toASCIIString(read_block(c, 10, 40)).strip('.')
    first_name = first_name_data.split("FIRSTNAME:")[1].capitalize()
    return first_name

def read_last_name_from_card(c):
    last_name_data = toASCIIString(read_block(c, 10, 41)).strip('.')
    last_name = last_name_data.split("LASTNAME:")[1].capitalize()
    return last_name

def read_balance_from_card(c):
    balance_data = toASCIIString(read_block(c, 10, 42)).strip('.')
    balance = balance_data.split("BALANCE:")[1]
    balance_dollars = int(balance.split('$')[0])
    balance_cents = int(balance.split('$')[1].split('c')[0])
    total_balance = (balance_dollars*100 + balance_cents) / 100
    return total_balance # float


def read_postcode_from_card(c):
    postcode_data = toASCIIString(read_block(c, 11, 44)).strip('.')
    postcode = postcode_data.split("POSTCODE:")[1]
    return postcode[:3] + " " + postcode[3:]

def read_pin_from_card(c):
    pincode_data = toASCIIString(read_block(c, 11, 45)).strip('.')
    pincode = pincode_data.split("PINCODE:")[1]
    return pincode

def read_birthdate_from_card(c):
    birthdate_data = toASCIIString(read_block(c, 11, 46)).strip('.')
    birthdate = birthdate_data.split("BIRTH:")[1]
    return birthdate

def read_uid_from_card(c):
    uid = read_uid(c)
    if uid:
        return toHexString(uid)
    else:
        return "ERROR"

def remove_balance_from_card(c, value):
    return ""

