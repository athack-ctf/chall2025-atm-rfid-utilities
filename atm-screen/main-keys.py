import curses
import art
from smartcard.System import readers
import threading
import time
import traceback
import sys
import os
import rfid
import smartcard


ATM_WIDTH = 50
ATM_HEIGHT = 15


BOX_WIDTH = 35
BOX_HEIGHT = 9

KEYS = [ord('j'), ord('s'), ord('l'), ord('a'), ord('q'), ord('p'), ord('w'), ord('e')]

ADMIN_UID = [0xDE, 0xAD, 0xBE, 0xEF]


FLAG3_PRICE = 514

FLAG2 = "ATHACKCTF{FLAG2}"
FLAG3 = "ATHACKCTF{FLAG3}"

stop_event = threading.Event()
card_present = False


def reset():
    os.execl(sys.executable, sys.executable, *sys.argv)

def check_card_presence(stdscr, conn):
    """Thread function that continuously checks if the card is still present."""
    global card_present

    while not stop_event.is_set():
        try:
            conn.getATR()  # Just check if the connection is alive
        except Exception:
            # Card removed, update global flag
            if card_present:
                card_present = False
                stdscr.clear()
                stdscr.refresh()
                draw_alert(stdscr, "⚠️ CARD REMOVED! ⚠️", timeout=3)
                reset()

        time.sleep(0.1)



def wait_for_card():
    """Waits for a card to be inserted and returns the connection object."""
    r = readers()
    if not r:
        raise Exception("No smart card readers found.")

    reader = r[0]  # Use the first available reader
    connection = reader.createConnection()

    while True:
        time.sleep(0.2)
        try:
            connection.connect()  # Try to connect
            return connection  # Return the connection object
        except smartcard.Exceptions.NoCardException:
            pass  # Keep waiting until a card is inserted
        except Exception:
            # traceback.print_exc()
            # time.sleep(5)
            reset()




def draw_welcome_screen(stdscr):
    stdscr.clear()
    stdscr.box()

    # Get screen size
    height, width = stdscr.getmaxyx()

    start_x = (width - ATM_WIDTH) // 2
    start_y = (height - ATM_HEIGHT) // 2

    # Generate ASCII art for "ATM"
    atm_art = art.text2art("ATM", font="big")  # You can change the font

    # Convert ASCII art to a list of lines
    atm_lines = atm_art.split("\n")
    
    art_start_y = start_y + 2
    art_start_x = start_x + (ATM_WIDTH - max(len(line) for line in atm_lines)) // 2


    # Display ASCII art
    for i, line in enumerate(atm_lines):
        stdscr.addstr(art_start_y + i, art_start_x, line)

    # Insert Card Message
    msg = "Please Insert Your Card..."
    msg_x = (width - len(msg)) // 2
    stdscr.addstr(start_y + len(atm_lines) + 2, msg_x, msg, curses.A_BOLD)

    stdscr.refresh()




# Function to display the ATM interface
def draw_atm_screen(stdscr, menu):
    stdscr.clear()
    stdscr.box()
    # Get screen dimensions
    height, width = stdscr.getmaxyx()

    start_x = (width - ATM_WIDTH) // 2
    start_y = (height - ATM_HEIGHT) // 2

    # Display ATM screen content
    header = "=== @Hack Bank of Concordia ==="
    stdscr.addstr(start_y + 2, start_x + (ATM_WIDTH - len(header)) // 2, header)

    # Show options on the left
    for i, option in enumerate(menu[:4]):
        x_pos = start_x + 2
        y_pos = start_y + 4 + 2*i
        stdscr.addstr(y_pos, x_pos, f"< {option}")

    # Show options on the right
    for i, option in enumerate(menu[4:]):
        x_pos = start_x + ATM_WIDTH - 2 - len(option) - 2
        y_pos = start_y + 4 + 2*i
        if i != 3:
            stdscr.addstr(y_pos, x_pos, f"{option} >")
        elif i == 3:
            stdscr.addstr(y_pos, x_pos, f"{option} >")

    stdscr.refresh()



def draw_alert(stdscr, message, timeout=0):
    curses.flushinp()
    height, width = stdscr.getmaxyx()

    # Alert box size
    box_width = BOX_WIDTH
    box_height = BOX_HEIGHT
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    win = curses.newwin(box_height, box_width, stdscr.getbegyx()[0] + start_y, stdscr.getbegyx()[1] + start_x)
    win.box()

    # Display the message centered inside the box
    if isinstance(message, list):
        for j, line in enumerate(message):
            win.addstr(j + 1, (box_width - len(line)) // 2, line)
    else:
        win.addstr(1, (box_width - len(message)) // 2, message)

    # OK button centered at the bottom
    button_field = "  OK  "
    button_x = (box_width  - len(button_field)) // 2
    button_y = box_height - 2
    win.addstr(button_y, button_x, button_field, curses.A_REVERSE)

    win.refresh()

    start_time = time.time()
    # Wait for user to press Enter before closing the alert
    while True:
        if timeout > 0:
            stdscr.nodelay(True)
            key = stdscr.getch()
            stdscr.nodelay(False)

            elapsed = time.time() - start_time
            time.sleep(0.01)
            if elapsed > timeout:
                curses.flushinp()
                break
            if key in [10, 13, ord('k')]:  # Enter key
                curses.flushinp()
                break
        else:
            key = stdscr.getch()
            if key in [10, 13, ord('k')]:  # Enter key
                curses.flushinp()
                break



def draw_pin_box(stdscr, name):
    """Displays a PIN entry box overlay on top of the existing menu."""
    height, width = stdscr.getmaxyx()

    # Create a centered overlay window
    box_width = BOX_WIDTH
    box_height = BOX_HEIGHT
    start_y = (height - box_height) // 2
    start_x = (width - box_width) // 2
    win = curses.newwin(box_height, box_width, stdscr.getbegyx()[0] + start_y, stdscr.getbegyx()[1] + start_x)
    win.box()

    # Display the prompt message
    win.addstr(1, 2, f"Hello {name}!")
    win.addstr(2, 2, "Tap pin to access:")
    
    # PIN entry field
    pin = ""
    max_pin_length = 4

    input_field = "[         ]"
    input_y = box_height - 3
    input_x = (box_width - len(input_field)) // 2
    win.addstr(input_y, input_x, input_field)  # Visual PIN box
    win.refresh()

    while True:
        key = stdscr.getch()
        
        if key in range(ord('0'), ord('9') + 1):  # If a number is typed
            if len(pin) < max_pin_length:
                pin += chr(key)
                win.addstr(input_y, input_x + len(pin)*2, "*")  # Show '*'
                win.refresh()

        elif key in [curses.KEY_BACKSPACE, 127, ord('h')]:  # Handle backspace
            if pin:
                pin = pin[:-1]
                win.addstr(input_y, input_x + len(pin)*2 + 2, " ")  # Clear last '*'
                win.refresh()

        elif key in [10, 13, ord('k')]:  # Enter key
            if len(pin) == 4:
                return pin  # Return the entered PIN
        

def draw_menu(stdscr, menu):
    # while True:
    draw_atm_screen(stdscr, menu)
    key = stdscr.getch()

    if key in KEYS:
        index = KEYS.index(key)
        choice = menu[index]
        # draw_alert(stdscr, f"Selected key {choice}")
        return choice


def draw_credits(stdscr, credit_text):
    """Draws end credit scrolling text with vertical bars on the side."""
    # Create the credit window with the provided long text
    stdscr.clear()
    stdscr.box()

    total_lines = len(credit_text)

    # Simulate falling vertical bars
    bar_position = ['|'] * ATM_HEIGHT  # Initial bar positions
    
    height, width = stdscr.getmaxyx()

    start_y = (height - ATM_HEIGHT) // 2
    start_x = (width - ATM_WIDTH) // 2

    win = curses.newwin(ATM_HEIGHT, ATM_WIDTH, stdscr.getbegyx()[0] + start_y, stdscr.getbegyx()[1] + start_x)

    # Initial y position for scrolling text
    y_position = ATM_HEIGHT
    bar_index = 0

    while True:
        win.clear()
        
        # Update the falling vertical bars, moving them down slowly
        for i in range(ATM_HEIGHT):
            if i % 4 != bar_index % 4:  # Slow down the falling bars every 3 lines
                bar_position[i] = '|'
            else:
                bar_position[i] = ' '
        
        # Draw the credit text scrolling from bottom to top
        for i, line in enumerate(credit_text):
            if (y_position + i) > 0 and (y_position + i) < ATM_HEIGHT - 1:
                win.addstr(y_position + i, (ATM_WIDTH - len(line)) // 2, line)  # Add some padding to the left side

        # Draw the falling bars
        for i in range(len(bar_position)):
            win.addstr(i, ATM_WIDTH - 2, bar_position[i])
            win.addstr(i, 0, bar_position[i])

            win.addstr(i, ATM_WIDTH - 3, bar_position[(i+1)%ATM_HEIGHT])
            win.addstr(i, 1, bar_position[(i+1)%ATM_HEIGHT])

        # Scroll the text by one line upwards
        y_position -= 1
        
        # If we reached the top, restart the scroll
        if y_position < -1*len(credit_text):
            break
        
        win.refresh()

        bar_index += 1
        time.sleep(0.35)  # Slow down the scrolling to make it visible



def authenticate_with_code(stdscr, c):
    name = rfid.read_first_name_from_card(c)

    for i in range(3):
        curses.flushinp()

        input_pin = draw_pin_box(stdscr, name)
        real_pin = rfid.read_pin_from_card(c)
        if input_pin == real_pin:
            return True
        else:
            draw_alert(stdscr, ["ERROR: WRONG PIN", "", f"{2-i} tries remaining."])
    
    return False



# Main function
def main(stdscr):
    global card_present
    card_present = False

    try:
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(False)   # Wait for user input
        # curses.resizeterm(200, 200)
        # stdscr.keypad(1)    # Enable arrow keys

        # Center ATM window inside terminal
        term_height, term_width = stdscr.getmaxyx()
        start_y = (term_height - ATM_HEIGHT) // 2
        start_x = (term_width - ATM_WIDTH) // 2
        atm_win = curses.newwin(ATM_HEIGHT, ATM_WIDTH, start_y, start_x)

        draw_welcome_screen(atm_win)

        c = wait_for_card()
        card_present = True

        # Start card presence monitoring in a separate thread
        monitor_thread = threading.Thread(target=check_card_presence, args=(atm_win, c), daemon=True)
        monitor_thread.start()
    
        
        if authenticate_with_code(atm_win, c):
            while True:
                root_menu = ["Balance", "Withdrawal", "Deposit", "Transfer", "Settings", "", "", "<Exit>"]

                user_choice = draw_menu(atm_win, root_menu)                
                match user_choice:
                    
                    # Balance
                    case "Balance":
                        user_funds = rfid.read_balance_from_card(c)
                        draw_alert(atm_win, message=f"Your have {user_funds}$.")
                 
                    # Withdraw
                    case "Withdrawal":
                        while True:
                            withdrawal_menu = ["10$", "20$", "42$", "1337$", "The Flag!?", "", "", "<Back>"]
                            user_choice = draw_menu(atm_win, withdrawal_menu)

                            match user_choice:
                                case "The Flag!?":
                                    user_funds = rfid.read_balance_from_card(c)
                                    if user_funds < FLAG3_PRICE:
                                        draw_alert(atm_win, message=["The flag is priceless...", "", f"(ok fine, I'll sell it for {FLAG3_PRICE}$)"])
                                    else:
                                        # remove_balance_from_card(c, FLAG3_PRICE)
                                        ## TODO Replace with print flag.
                                        draw_alert(atm_win, message=["Congrats, @Hacker!", "You are now the proud", "owner of a flag!", f"Printing receipt..."], timeout=5)
                                        pass
                                    
                                case "<Back>":
                                    break

                                case "":
                                    continue

                                case _:
                                    withdraw_value = int(user_choice[:-1])
                                    user_funds = rfid.read_balance_from_card(c)
                                    if withdraw_value > user_funds:
                                        draw_alert(atm_win, message="Not enough funds on card :(")
                                    else:
                                        draw_alert(atm_win, message=["You know it's not", "a real ATM, right?"])

                    # Deposit
                    case "Deposit":
                        draw_alert(atm_win, message="Not available.")

                    # Transfer
                    case "Transfer":
                        draw_alert(atm_win, message="Not available.")

                    case "Settings":
                        while True:
                            settings_menu = ["Profile", "Credits", "Admin Menu", "", "", "", "", "<Back>"]
                            user_choice = draw_menu(atm_win, settings_menu)

                            match user_choice:
                                case "Profile":
                                    first_name = rfid.read_first_name_from_card(c)
                                    last_name = rfid.read_last_name_from_card(c)
                                    birthdate = rfid.read_birthdate_from_card(c)
                                    postal_code = rfid.read_postcode_from_card(c)
                                    uid = rfid.read_uid_from_card(c)
                                    pincode = rfid.read_pin_from_card(c)

                                    draw_alert(atm_win, [f"First Name: {first_name}",
                                                        f"Last Name: {last_name}",
                                                        f"Birthdate: {birthdate}",
                                                        f"Postal Code: {postal_code}",
                                                        f"UID: {uid}",
                                                        f"Pincode: {pincode}"])

                                case "Credits":
                                    credits = open(os.path.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))), "credits.txt")).readlines()
                                    draw_credits(atm_win, credits)

                                case "Admin Menu":
                                    user_uid = rfid.read_uid_from_card(c)
                                    draw_alert(atm_win, f"UID: {user_uid}")
                                    if user_uid != ADMIN_UID:
                                        draw_alert(atm_win, "You are not the admin!")
                                    else:
                                        draw_alert(atm_win, ["I know you'd come, Roger...", f"{FLAG2}"])

                                case "<Back>":
                                    break

                                case "":
                                    continue

                    # Exit
                    case "<Exit>":
                        reset()
                    
                    case _:
                        pass
        # Wrong auth
        else:
            reset()
                
    except rfid.WrongKeyException as e:
        draw_alert(atm_win, ["ERROR: Wrong key.", "", "Please use default keys."], timeout=4)
        reset()

    except Exception as e:
        traceback.print_exc()
        time.sleep(5)
        stdscr.clear()
        stdscr.refresh()
        reset() # Restart the main function

if __name__ == "__main__":
    curses.wrapper(main)
