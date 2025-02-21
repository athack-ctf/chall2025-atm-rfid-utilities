import curses
import art

atm_width = 50
atm_height = 15


def draw_welcome_screen(stdscr):
    stdscr.clear()

    # Get screen size
    height, width = stdscr.getmaxyx()

    start_x = (width - atm_width) // 2
    start_y = (height - atm_height) // 2

    # draw border
    stdscr.addstr(start_y, start_x, "+" + "-" * (atm_width - 2) + "+")
    for i in range(1, atm_height - 1):
        stdscr.addstr(start_y + i, start_x, "|" + " " * (atm_width - 2) + "|")
    stdscr.addstr(start_y + atm_height - 1, start_x, "+" + "-" * (atm_width - 2) + "+")

    # Generate ASCII art for "ATM"
    atm_art = art.text2art("ATM", font="big")  # You can change the font

    # Convert ASCII art to a list of lines
    atm_lines = atm_art.split("\n")
    
    art_start_y = start_y + 2
    art_start_x = start_x + (atm_width - max(len(line) for line in atm_lines)) // 2


    # Display ASCII art
    for i, line in enumerate(atm_lines):
        stdscr.addstr(art_start_y + i, art_start_x, line)

    # Insert Card Message
    msg = "Please Insert Your Card..."
    msg_x = (width - len(msg)) // 2
    stdscr.addstr(start_y + len(atm_lines) + 2, msg_x, msg, curses.A_BOLD)

    # Prompt for user input
    prompt = "Press [ENTER] to continue..."
    prompt_x = (width - len(prompt)) // 2
    stdscr.addstr(start_y + len(atm_lines) + 4, prompt_x, prompt, curses.A_REVERSE)

    stdscr.refresh()

    # Wait for user to press Enter
    while True:
        key = stdscr.getch()
        if key in [10, 13]:  # Enter key
            break



# Function to display the ATM interface
def draw_atm_screen(stdscr, menu, selected_left, selected_right, side):
    stdscr.clear()

    # Get screen dimensions
    height, width = stdscr.getmaxyx()

    start_x = (width - atm_width) // 2
    start_y = (height - atm_height) // 2

    # Draw ATM border
    for i in range(atm_height):
        stdscr.addstr(start_y + i, start_x, "|" + " " * (atm_width - 2) + "|")
    stdscr.addstr(start_y, start_x, "+" + "-" * (atm_width - 2) + "+")
    stdscr.addstr(start_y + atm_height - 1, start_x, "+" + "-" * (atm_width - 2) + "+")

    # Display ATM screen content
    header = "=== @Hack Bank of Concordia ==="
    stdscr.addstr(start_y + 2, start_x + (atm_width - len(header)) // 2, header)

    # Show options on the left
    for i, option in enumerate(menu[:4]):
        x_pos = start_x - 10
        y_pos = start_y + 4 + 2*i
        if side == "left" and i == selected_left:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(y_pos, x_pos, f"< {option}")
        if side == "left" and i == selected_left:
            stdscr.attroff(curses.A_REVERSE)

    # Show options on the right
    for i, option in enumerate(menu[4:]):
        x_pos = start_x + atm_width + 2
        y_pos = start_y + 4 + 2*i
        if side == "right" and i == selected_right:
            stdscr.attron(curses.A_REVERSE)
        stdscr.addstr(y_pos, x_pos, f"{option} >")
        if side == "right" and i == selected_right:
            stdscr.attroff(curses.A_REVERSE)

    stdscr.refresh()

def draw_alert(stdscr, message):
    stdscr.clear()
    
    # Get screen dimensions
    height, width = stdscr.getmaxyx()
    
    # Alert box size
    box_width = 40
    box_height = 7
    start_x = (width - box_width) // 2
    start_y = (height - box_height) // 2

    # Draw box border
    stdscr.addstr(start_y, start_x, "+" + "-" * (box_width - 2) + "+")
    for i in range(1, box_height - 1):
        stdscr.addstr(start_y + i, start_x, "|" + " " * (box_width - 2) + "|")
    stdscr.addstr(start_y + box_height - 1, start_x, "+" + "-" * (box_width - 2) + "+")

    # Display the message centered inside the box
    msg_x = start_x + (box_width - len(message)) // 2
    stdscr.addstr(start_y + 2, msg_x, message)

    # OK button centered at the bottom
    ok_x = start_x + (box_width - 6) // 2  # Centering [ OK ]
    stdscr.attron(curses.A_REVERSE)
    stdscr.addstr(start_y + box_height - 2, ok_x, "  OK  ")
    stdscr.attroff(curses.A_REVERSE)

    stdscr.refresh()

    # Wait for user to press Enter before closing the alert
    while True:
        key = stdscr.getch()
        if key in [10, 13]:  # Enter key
            break

     

def draw_menu(stdscr, menu):
    selected_left = 0
    selected_right = 0

    side = "left"  # Start selection on the left menu

    while True:
            draw_atm_screen(stdscr, menu, selected_left, selected_right, side)
            key = stdscr.getch()

            if key == curses.KEY_UP:
                if side == "left" and selected_left > 0:
                    selected_left -= 1
                elif side == "right" and selected_right > 0:
                    selected_right -= 1
            elif key == curses.KEY_DOWN:
                if side == "left" and selected_left < len(menu[:4]) - 1:
                    selected_left += 1
                elif side == "right" and selected_right < len(menu[4:]) - 1:
                    selected_right += 1
            elif key == curses.KEY_LEFT:
                side = "left"
                selected_left = selected_right
            elif key == curses.KEY_RIGHT:
                side = "right"
                selected_right = selected_left
            elif key in [10, 13]:  # Enter key
                choice = menu[selected_left] if side == "left" else menu[4+selected_right]
                return choice


# Main function
def atm_simulator(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(0)   # Wait for user input
    stdscr.keypad(1)    # Enable arrow keys

    
    draw_welcome_screen(stdscr)
    

    root_menu = ["Balance", "Withdraw", "Deposit", "Exit", "Transfer", "Settings", "Help", "Exit"]

    user_choice = draw_menu(stdscr, root_menu)
    if user_choice == "Withdraw":
        withdraw_menu = ["10$", "20$", "42$", "1000$", "The Flag!?", "16$", "5$", "32$"]
        user_choice = draw_menu(stdscr, withdraw_menu)

        if user_choice == "The Flag!?": # flag
            draw_alert(stdscr, message="Damn brother!")
        else:
            withdraw_value = int(user_choice)
    

# Run the ATM simulation
curses.wrapper(atm_simulator)
