# diagnostic.py
import board
import busio
import digitalio
import adafruit_ahtx0
from adafruit_seesaw.seesaw import Seesaw

def test_pins():
    try:
        # Define pins
        pins = {
            'S1': board.D13,
            'S2': board.D16,
            'S3': board.D19,
            'S4': board.D20,
            'S5': board.D26,
            'S6': board.D21,
            'B1': board.D10,
            'QWIIC_SCL': board.SCL,
            'QWIIC_SDA': board.SDA
        }
        
        # Test actuator circuits
        for pin_name in ['S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'B1']:
            pin = digitalio.DigitalInOut(pins[pin_name])
            print(f"Pin {pin_name} initialized successfully")
        
        # Setup QWIIC Bus
        qwiic = busio.I2C(scl=pins['QWIIC_SCL'], sda=pins['QWIIC_SDA'])
        print("QWIIC bus initialized successfully")

        # Test sensors
        ths = adafruit_ahtx0.AHTx0(qwiic)  # Temperature & Humidity Sensor
        print("Temperature & Humidity Sensor initialized successfully")
        
        sms = Seesaw(qwiic, addr=0x36)  # Soil Moisture Sensor
        print("Soil Moisture Sensor initialized successfully")
        
        return True
    except Exception as e:
        print(f"Initialization failed: {e}")
        return False

if __name__ == "__main__":
    result = test_pins()
    if result:
        print("All components initialized successfully")
    else:
        print("Some components failed to initialize")
