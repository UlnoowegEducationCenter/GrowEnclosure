import board
import time
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C
from addclass import PlantDef  # Ensure this import statement matches your setup

# Initialize the plant
testPlant = PlantDef(
    name='testPlant',
    dryValue=800,
    maxTemp=30,
    maxHumid=90,
    waterVol=600,
    checkTime=(12, 00),
    sunrise=(7, 00),
    sunset=(19, 00)
)

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
    lcd.clear()
    lcd.message = f"{parameter_name}: {value}\nUp/Down to change"
    adjusting = True
    while adjusting:
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            value = min(value + step, max_val)
            lcd.message = f"{parameter_name}: {value}\nUp/Down to change"
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            value = max(value - step, min_val)
            lcd.message = f"{parameter_name}: {value}\nUp/Down to change"
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            setattr(testPlant, parameter_name, value)
            lcd.clear()
            lcd.message = f"{parameter_name} set to {value}"
            time.sleep(1)  # Show the set message
            adjusting = False
        time.sleep(0.2)  # Reduce refresh rate to minimize jitter

def main_menu():
    """Function to navigate between different settings."""
    options = ['Max Humid', 'Water Vol']
    index = 0
    lcd.message = f"Select: {options[index]}"
    while True:
        if lcd.up_button:
            debounce(lambda: lcd.up_button)
            index = (index - 1) % len(options)
            lcd.message = f"Select: {options[index]}"
        elif lcd.down_button:
            debounce(lambda: lcd.down_button)
            index = (index + 1) % len(options)
            lcd.message = f"Select: {options[index]}"
        elif lcd.select_button:
            debounce(lambda: lcd.select_button)
            if options[index] == 'Max Humid':
                adjust_parameter('maxHumid', 5, 0, 100)
            elif options[index] == 'Water Vol':
                adjust_parameter('waterVol', 10, 0, 1000)
            lcd.clear()
            lcd.message = f"Select: {options[index]}"

# Main loop
while True:
    lcd.clear()
    lcd.message = "Press Select to\nenter settings"
    if lcd.select_button:
        debounce(lambda: lcd.select_button)
        main_menu()
