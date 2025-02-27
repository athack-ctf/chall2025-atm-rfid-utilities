from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardConnection import CardConnection
import time
import random
import smartcard


KEY_A = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
KEY_NUMBER = 0x00
# TARGET_UID = [0xDE, 0xAD, 0xBE, 0xEF]

# ATHACKCTF{0kN0wH4ckTh3ATM!!} in base64
# QVRIQUNLQ1RGezBrTjB3SDRja1RoM0FUTSEhfQ==
# PAD with 0, split in 3 group of 16
FLAG1_1 = [0x51,0x56,0x52,0x49, 0x51,0x55,0x4e,0x4c, 0x51,0x31,0x52,0x47, 0x65,0x7a,0x42,0x72]
FLAG1_2 = [0x54,0x6a,0x42,0x33, 0x53,0x44,0x52,0x6a, 0x61,0x31,0x52,0x6f, 0x4d,0x30,0x46,0x55]
FLAG1_3 = [0x54,0x53,0x45,0x68, 0x66,0x51,0x3d,0x3d, 0x00,0x00,0x00,0x00, 0x00,0x00,0x00,0x00]


def get_reader():
    """Get the first available reader."""
    available_readers = readers()
    if not available_readers:
        raise Exception("No card reader found")
    return available_readers[0]

def load_keyA(connection):
    """Load a key into ACR122U's key storage"""
    load_key_apdu = [0xFF, 0x82, 0x00, KEY_NUMBER, 0x06] + KEY_A
    response, sw1, sw2 = connection.transmit(load_key_apdu)
    if sw1 == 0x90 and sw2 == 0x00:
        return True
    else:
        print(f"Loading key failed. SW1: {sw1}, SW2: {sw2}")
        return False


def authenticate_with_keyA(connection, sector):
    """Authenticate using Key A on a specific sector."""
    block = sector * 4 # last block of sector
    command = [0xFF, 0x86, 0x00, KEY_NUMBER, 0x05, 0x01, 0x00, block, 0x60, 0x00]
    response, sw1, sw2 = connection.transmit(command)
    if sw1 == 0x90 and sw2 == 0x00:
        print(f"Authentication Success sector {sector}")
        return True
    else:
        print(f"Authentication failed. SW1: {sw1}, SW2: {sw2}")
        exit(0)
        return False



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
        print(f"Failed to read block {block}. SW1: {sw1}, SW2: {sw2}")
        return None


def write_block(connection, sector, block, data):
    """Write 16 bytes of data to a specific block in a sector."""
    if not authenticate_with_keyA(connection, sector):
        return False

    if (block % 4) == 3:
        print("CAREFUL: overwriting key/ACL block?")
        return False
    
    # Check if data is 16 bytes long
    if len(data) != 16:
        print("Data must be exactly 16 bytes long.")
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

def wait_for_card():
    """Waits for a card to be inserted and returns the connection object."""
    r = readers()
    if not r:
        raise Exception("No smart card readers found.")

    reader = r[0]  # Use the first available reader
    connection = reader.createConnection()

    while True:
        time.sleep(0.5)
        print("waiting for card")
        try:
            connection.connect()  # Try to connect
            return connection  # Return the connection object
        except smartcard.Exceptions.NoCardException:
            pass  # Keep waiting until a card is inserted
        except Exception:
            # traceback.print_exc()
            # time.sleep(5)
            reset()


def main():

    while True:

        try:
            connection = wait_for_card()

            # # Get the first available reader
            # reader = get_reader()
            # connection = reader.createConnection()
            # connection.connect()

            uid = read_uid(connection)
            if uid:
                print(f"UID: {toHexString(uid)}")

            load_keyA(connection)

            #### FLAG 1 JUST ENCODED IN THE CARD, SECTOR 1
            sector = 1

            # FLAG1_1 in block 4
            block = 4
            if write_block(connection, sector, block, FLAG1_1):
                print("Data written successfully!")

            # FLAG1_2 in block 5
            block = 5
            if write_block(connection, sector, block, FLAG1_2):
                print("Data written successfully!")

            # FLAG1_3 in block 6
            block = 6
            if write_block(connection, sector, block, FLAG1_3):
                print("Data written successfully!")
                

            # # EXTRAFLAG?
            # sector = 3
            # block = 12 # and 13 and 14
            # if write_block(connection, sector, block, EXTRAFLAG_1):
            #     print("Data written successfully!")




            #### DATA FOR FLAG 3 AT SECTOR 10
            sector = 10

            # FIRSTNAME:NED
            block = 40
            first_name  = [0x46,0x49,0x52,0x53, 0x54,0x4e,0x41,0x4d, 0x45,0x3a,0x4e,0x45, 0x44,0x00,0x00,0x00]
            if write_block(connection, sector, block, first_name):
                print("Data written successfully!")

            # LASTNAME:???
            block = 41
            last_name   = [0x4c,0x41,0x53,0x54, 0x4e,0x41,0x4d,0x45, 0x3a,0x3f,0x3f,0x3f, 0x00,0x00,0x00,0x00]
            if write_block(connection, sector, block, last_name):
                print("Data written successfully!")

            # BALANCE:0015$80c
            block = 42
            balance     = [0x42,0x41,0x4c,0x41, 0x4e,0x43,0x45,0x3a, 0x30,0x30,0x31,0x35, 0x24,0x38,0x30,0x63]
            if write_block(connection, sector, block, balance):
                print("Data written successfully!")


            #### CONTINUE DATA FOR FLAG 3 AT SECTOR 11
            sector = 11

            # POSTCODE:H3G1M8
            block = 44
            postal_code     = [0x50,0x4f,0x53,0x54, 0x43,0x4f,0x44,0x45, 0x3a,0x48,0x33,0x47, 0x31,0x4d,0x38,0x00]
            if write_block(connection, sector, block, postal_code):
                print("Data written successfully!")

            # PINCODE:XXXX
            block = 45
            random.seed(time.time_ns())
            pin_code = ""
            for i in range(4):
                pin_code += str(random.randrange(10))
            print("Pin Code: ", pin_code)
            pin_code_data   = [0x50,0x49,0x4e,0x43, 0x4f,0x44,0x45,0x3a] + list(bytearray(pin_code, 'utf-8')) + [0x00,0x00,0x00,0x00]
            print("Pin data: ", pin_code_data)
            if write_block(connection, sector, block, pin_code_data):
                print("Data written successfully!")

            # BIRTH:30/06/1998
            block = 46
            birthdate     = [0x42,0x49,0x52,0x54,0x48,0x3a,0x33,0x30,0x2f,0x30,0x36,0x2f,0x31,0x39,0x39,0x38]
            if write_block(connection, sector, block, birthdate):
                print("Data written successfully!")
            
            connection.disconnect()
            
            print("Remove card!")
            time.sleep(1.75)

        except Exception as e:
            pass

if __name__ == "__main__":
    main()