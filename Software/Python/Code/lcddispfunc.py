import board
import time
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C
from addclass import testPlant  # Ensure this import statement matches your setup


i2c = board.I2C()  # uses board.SCL and board.SDA
lcd = Character_LCD_RGB_I2C(i2c, 16, 2)

def debounce(button):
    """ Debounce a button property """
    button_state = button()  # Initial state
    last_change_time = time.monotonic()
    while True:
        current_time = time.monotonic()
        if button() != button_state:
            last_change_time = current_time
        button_state = button()
        if current_time - last_change_time > 0.1:  # Wait for stable state for 100ms
            break
    return button_state

def adjust_parameter(parameter_name, step, min_val, max_val):
    """General function to adjust a numerical parameter."""
    value = getattr(testPlant, parameter_name)
    message = f"{parameter_name}: {value}  "
    lcd.message = message
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            value = min(value + step, max_val)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            value = max(value - step, min_val)
            update = True
        if update:
            message = f"{parameter_name}: {value}  "
            lcd.message = message
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            setattr(testPlant, parameter_name, value)
            message = f"Set to {value}    "
            lcd.message = message
            time.sleep(1)  # Show the set message
            break
        time.sleep(0.2)  # Reduce refresh rate to minimize jitter

def adjust_time_parameter(parameter_name):
    """Function to adjust time parameters (HH:MM)."""
    value = getattr(testPlant, parameter_name)
    hours, minutes = value
    message = f"{parameter_name}: {hours:02d}:{minutes:02d}  "
    lcd.message = message
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            hours = (hours + 1) % 24
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            hours = (hours - 1) % 24
            update = True
        elif lcd.right_button:
            debounce(lambda: lcd.right_button)
            minutes = (minutes + 1) % 60
            update = True
        elif lcd.left_button:
            debounce(lambda: lcd.left_button)
            minutes = (minutes - 1) % 60
            update = True
        if update:
            message = f"{parameter_name}: {hours:02d}:{minutes:02d}  "
            lcd.message = message
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            setattr(testPlant, parameter_name, (hours, minutes))
            message = f"Set to {hours:02d}:{minutes:02d}  "
            lcd.message = message
            time.sleep(1)  # Show the set message
            break
        time.sleep(0.2)  # Reduce refresh rate to minimize jitter

def display_menu(options, index):
    """Helper function to display menu options with the current selection on the bottom line."""
    lcd.clear()
    lcd.message = f"Select Option:\n{options[index][:16]}"

def main_menu():
    """Function to navigate between different settings."""
    options = ['Edit Settings', 'Manual Control']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Edit Settings':
                edit_settings_menu()
            elif options[index] == 'Manual Control':
                manual_control_menu()
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def edit_settings_menu():
    """Function to navigate and edit settings."""
    options = ['System Time', 'Sunrise Time', 'Sunset Time', 'Irrigation', 'Temp Setpoint', 'Humidity Setpoint', 'Camera Yes/No', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'System Time':
                adjust_time_parameter('checkTime')  # Adjust time
            elif options[index] == 'Sunrise Time':
                adjust_time_parameter('sunrise')  # Adjust time
            elif options[index] == 'Sunset Time':
                adjust_time_parameter('sunset')  # Adjust time
            elif options[index] == 'Irrigation':
                irrigation_menu()
            elif options[index] == 'Temp Setpoint':
                adjust_parameter('maxTemp', 1, 0, 50)
            elif options[index] == 'Humidity Setpoint':
                adjust_parameter('maxHumid', 5, 0, 100)
            elif options[index] == 'Camera Yes/No':
                # Add camera toggle functionality here
                pass
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def irrigation_menu():
    """Function to navigate and edit irrigation settings."""
    options = ['Soil Moist Thresh', 'Water Vol', 'Watering Time', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Soil Moist Thresh':
                adjust_parameter('dryValue', 10, 0, 1000)
            elif options[index] == 'Water Vol':
                adjust_parameter('waterVol', 10, 0, 1000)
            elif options[index] == 'Watering Time':
                adjust_time_parameter('checkTime')  # Adjust time
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

def manual_control_menu():
    """Function to handle manual controls."""
    options = ['Take Picture Now', 'Water Now', 'Light On Now', 'Fan On Now', 'Back']
    index = 0
    display_menu(options, index)
    while True:
        update = False
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            update = True
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            update = True
        if update:
            display_menu(options, index)
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Take Picture Now':
                # Add take picture functionality here
                pass
            elif options[index] == 'Water Now':
                # Add water now functionality here
                pass
            elif options[index] == 'Light On Now':
                # Add light on functionality here
                pass
            elif options[index] == 'Fan On Now':
                # Add fan on functionality here
                pass
            elif options[index] == 'Back':
                break
            display_menu(options, index)
            time.sleep(0.5)  # Pause before returning to menu

# Main loop
lcd.clear()
lcd.message = "Press Select to\nstart settings"
while True:
    if lcd.select_button:
        debounce(lambda: lcd.select_button)
        main_menu()
        lcd.clear()
        lcd.message = "Press Select to\nstart settings"
    time.sleep(0.2)  # Reduce the refresh rate to minimize flicker
