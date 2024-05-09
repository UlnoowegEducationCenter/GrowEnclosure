#Growth Enclosure lcd output Python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#V0.7
#For Adrafruit 1110
########################################

#Import important modules
import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

#Define LCD
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.cursor = False

#This function recieve text1 and text2 input for line 1 and line 2 (16 char each) and colour as a text: r g or b
def lcddisplay(text1, text2, colour_text): #define lcddisplay function to display text1 and text2 as line 1 and 2
    #Set colour based on incoming text
    if colour_text == 'r':
        lcd.color = [100, 0, 0]
    elif colour_text == 'g':
        lcd.color = [0,100,0]
    elif colour_text == 'b':
        lcd.color = [0,0,100]
    else:
        lcd.color = [100, 0, 0]
        lcd.cursor_position(0,0)
        lcd.message = "ERROR:"
        lcd.cursor_position(0,1)
        lcd.message = "LCD COLOUR FAIL"
        raise RuntimeError('LCD_COLOUR_ERROR')
    
    #Display output to lcd
    lcd.clear()
    lcd.cursor_position(0,0)
    lcd.message = text1
    lcd.cursor_position(0,1)
    lcd.message = text2
    
def lcddisplay_menu():
    lcd.clear()
    lcd.message = "1. Set Watering\n2. Set Schedule\n3. Exit"

    selected_option = 1  # Initialize the selected option

    while True:
        if lcd.up_button:
            # Handle up button press
            selected_option -= 1  # Move to the previous menu option
        elif lcd.down_button:
            # Handle down button press
            selected_option += 1  # Move to the next menu option
        elif lcd.select_button:
            # Handle select button press
            if selected_option == 1:
                set_watering_parameters()  # Call a function to set watering parameters
            elif selected_option == 2:
                set_schedule_parameters()  # Call a function to set schedule parameters
            elif selected_option == 3:
                return  # Exit the menu

        # Ensure the selected option stays within the menu range
        selected_option = max(1, min(selected_option, 3))

        # Update the LCD display with the current menu and selected option
        update_lcd_menu(selected_option)



        # time.sleep(0.2)  # Adjust sleep time as needed for button responsiveness

lcddisplay_menu()

def update_lcd_menu(selected_option):
    # Update the LCD display based on the selected option
    if selected_option == 1:
        lcd.message = "Set Watering\nVolume: XXX mL"  # Show current watering volume
    elif selected_option == 2:
        lcd.message = "Set Schedule\nCheck Time: hh:mm"  # Show current check time
    elif selected_option == 3:
        lcd.message = "Exit Menu"

def set_watering_parameters():
    # Logic to set watering parameters
    pass

def set_schedule_parameters():
    # Logic to set schedule parameters
    pass
