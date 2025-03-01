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

def read_block(connection, sector, block):
    """Read 16 bytes from a specific block in a sector using Key A."""
    if not authenticate_with_keyA(connection, sector):
        return None

    command = [0xFF, 0xB0, 0x00, block, 0x10]  # Read 16 bytes
    response, sw1, sw2 = connection.transmit(command)
    if sw1 == 0x90 and sw2 == 0x00:
        return response
    return None

def read_uid(connection):
    """Read UID (Block 0)."""
    apdu_read_uid = [0xFF, 0xCA, 0x00, 0x00, 0x04]
    response, sw1, sw2 = connection.transmit(apdu_read_uid)
    return response if sw1 == 0x90 and sw2 == 0x00 else None

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

def check_card_data(connection):
    """Check if the card has been written to and display the details."""
    uid = read_uid(connection)
    if not uid:
        print("Failed to read card UID.")
        return False
    print(f"Card UID: {toHexString(uid)}")
    
    data_found = False
    
    for sector in range(1, 12):  # Scan sectors 1 to 11
        for block in range(sector * 4, sector * 4 + 3):  # Skip sector trailer blocks
            data = read_block(connection, sector, block)
            if data and any(byte != 0x00 for byte in data):  # Check if block has data
                data_found = True
                print(f"Sector {sector}, Block {block}: {bytes(data).decode(errors='ignore')}")
    
    if not data_found:
        print("No data found on card.")
    
    return data_found

def main():
    while True:
        try:
            connection = wait_for_card()
            print("Card detected!")
            check_card_data(connection)
            connection.disconnect()
            print("Remove card!")
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
