from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.CardConnection import CardConnection
import smartcard
import time

def get_reader():
    """Get the first available reader."""
    available_readers = readers()
    if not available_readers:
        raise Exception("No card reader found")
    return available_readers[0]

def authenticate_with_keyA(connection, sector, key=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]):
    """Authenticate using Key A on a specific sector."""
    block = sector * 4  # First block of the sector
    command = [0xFF, 0x86, 0x00, 0x00, 0x05, 0x01, 0x00, block, 0x60, 0x00]
    response, sw1, sw2 = connection.transmit(command)
    return sw1 == 0x90 and sw2 == 0x00

def write_block(connection, sector, block, data):
    """Write 16 bytes of zero data to a specific block in a sector."""
    if not authenticate_with_keyA(connection, sector):
        return False
    
    if (block % 4) == 3:
        print("Skipping sector trailer block to avoid bricking the card.")
        return False
    
    command = [0xFF, 0xD6, 0x00, block, 0x10] + data
    response, sw1, sw2 = connection.transmit(command)
    return sw1 == 0x90 and sw2 == 0x00

def reset_card(connection):
    """Reset the card by overwriting all writable blocks with zeros."""
    zero_data = [0x00] * 16
    
    for sector in range(1, 12):  # Reset sectors 1 to 11
        for block in range(sector * 4, sector * 4 + 3):  # Skip sector trailer
            if write_block(connection, sector, block, zero_data):
                print(f"Reset Sector {sector}, Block {block} successfully.")
            else:
                print(f"Failed to reset Sector {sector}, Block {block}.")

def wait_for_card():
    """Wait for a card to be inserted and return the connection object."""
    r = readers()
    if not r:
        print("No smart card readers found. Waiting for connection...")
        while not r:
            time.sleep(1)
            r = readers()
    
    reader = r[0]
    connection = reader.createConnection()
    while True:
        time.sleep(1)
        print("Waiting for card...")
        try:
            connection.connect()
            return connection
        except smartcard.Exceptions.NoCardException:
            pass

def main():
    while True:
        try:
            connection = wait_for_card()
            print("Card detected! Resetting...")
            reset_card(connection)
            connection.disconnect()
            print("Card reset successfully! Remove the card.")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
