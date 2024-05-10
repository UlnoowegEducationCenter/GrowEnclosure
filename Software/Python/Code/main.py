import board
import busio
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd
import time

# Setup LCD
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)
lcd.cursor = False

def lcddisplay(text1, text2, colour_text):
    try:
        if colour_text == 'r':
            lcd.color = [100, 0, 0]
        elif colour_text == 'g':
            lcd.color = [0, 100, 0]
        elif colour_text == 'b':
            lcd.color = [0, 0, 100]
        else:
            lcd.color = [100, 0, 0]
            lcd.message = "ERROR: LCD COLOUR FAIL"
            raise RuntimeError('LCD_COLOUR_ERROR')
    
        lcd.clear()
        lcd.message = f"{text1}\n{text2}"
    except Exception as e:
        print(f"Error: {str(e)}")

def run():
    try:
        print("Starting the display menu...")
        lcddisplay_menu()
    except Exception as e:
        print(f"Run-time error: {str(e)}")

def lcddisplay_menu():
    lcd.clear()
    lcd.message = "1. Set Watering\n2. Set Schedule\n3. Exit"
    selected_option = 1

    while True:
        print(f"Current option: {selected_option}")  # Debug statement
        time.sleep(1)  # Simulate delay for button press handling
        
        # Here, add actual button press detection logic
        # For testing without buttons, you can simulate a button press or break after a loop iteration
        break  # Remove this in actual use

        # Add button logic here

if __name__ == '__main__':
    run()
