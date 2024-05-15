# Growth Enclosure main Python code
# Ulnooweg Education Centre - All rights reserved
# Contact: ulnoowegeducation.ca

# V0.7
########################################

# Import important libraries
import asyncio
import time
import json

# Additional Python Libraries
from Adafruit_IO import Client, RequestError, Group
from lcddispfunc import lcddisplay, main_menu

# All these are part of Blinka
import board
import busio
import digitalio

# Library requiring additional installation other than standard Blinka install
import adafruit_ahtx0
from adafruit_seesaw.seesaw import Seesaw
import adafruit_ina219
import adafruit_character_lcd.character_lcd_rgb_i2c as character_lcd

# Functions/Class from other files
from addclass import testPlant  # import testPlant as specific instance of the Plantdef class from addclass

# Configure global parameters for various options in the code
rateLimit = 30  # Adafruit IO updates per minute
plant = testPlant  # which plant are we growing

# Setup pinouts for hardware used
# Current: Raspberry Pi 3 A+ with BCRobotics Irrigation Hat V2
# LCD Definitions
lcd_columns = 16
lcd_rows = 2
i2c = busio.I2C(board.SCL, board.SDA)
lcd = character_lcd.Character_LCD_RGB_I2C(i2c, lcd_columns, lcd_rows)

# For Blinka, the pins are defined as DXX
pins = {
    'S1': board.D13,  # This is MOSFET control pin 1 (System 1). Other S pin controls n MOSFET.
    'S2': board.D16,  # DXX Corresponds to GPIO pins XX
    'S3': board.D19,
    'S4': board.D20,
    'S5': board.D26,
    'S6': board.D21,
    'B1': lcd.up_button,  # This is button input using LCD up button handled via adafruit i2c lcd lib
    'B2': lcd.down_button,
    'B3': lcd.left_button,
    'B4': lcd.right_button,
    'B5': lcd.select_button,
    'QWIIC_SCL': board.SCL,  # Define I2C pin CLOCK, use board.SCL in pi
    'QWIIC_SDA': board.SDA  # Define I2C pin DATA, use board.SDA in pi
}

# Setup Actuator circuits
print("initializing actuator circuits")
lcddisplay('SETUP', 'ACTUATE CIR INIT', 'b')

s1 = digitalio.DigitalInOut(pins['S1'])
s2 = digitalio.DigitalInOut(pins['S2'])
s3 = digitalio.DigitalInOut(pins['S3'])
s4 = digitalio.DigitalInOut(pins['S4'])
s5 = digitalio.DigitalInOut(pins['S5'])
s6 = digitalio.DigitalInOut(pins['S6'])

for s in [s1, s2, s3, s4, s5, s6]:
    s.direction = digitalio.Direction.OUTPUT
    s.drive_mode = digitalio.DriveMode.PUSH_PULL
    s.value = False

# Setup QWIIC Bus
print("initializing I2C bus")
lcddisplay('SETUP', 'I2C BUS INIT', 'b')
qwiic = busio.I2C(scl=pins['QWIIC_SCL'], sda=pins['QWIIC_SDA'])

# Setup Sensors
print("initializing sensors")
lcddisplay('SETUP', 'SENSORS INIT', 'b')
try:
    ths = adafruit_ahtx0.AHTx0(qwiic)  # Temperature & Humidity Sensor
    sms = Seesaw(qwiic, addr=0x36)  # Soil Moisture Sensor
    cs = adafruit_ina219.INA219(qwiic)  # Pump Current Sensor
except:
    print("UNABLE TO INITIALIZE SENSORS; RELOADING")
    lcddisplay('ERROR', 'SENSOR INIT FAIL', 'r')
    raise RuntimeError('SENSOR ERROR')
    # The code will reboot by the forced restart systemd flag after error is raised and the code exited

# Creating actuator objects
class Actuator:
    def __init__(self, circuit, button_type, default=False, flowRate=None, minCurrent=None):
        self.circuit = circuit
        self.button_type = button_type
        self.default = default
        self.flowRate = flowRate
        self.minCurrent = minCurrent

    def buttonInput(self):
        if self.button_type == 'up':
            if lcd.up_button:
                self.circuit.value = True
        elif self.button_type == 'down':
            if lcd.down_button:
                self.circuit.value = True
        elif self.button_type == 'left':
            if lcd.left_button:
                self.circuit.value = True
        else:
            self.circuit.value = self.default
        return

pump = Actuator(circuit=s1, button_type='up', flowRate=66.7, minCurrent=600)
light = Actuator(circuit=s2, button_type='down')
fan = Actuator(circuit=s3, button_type='left')

# Open file with 'with' statement as json_file. This autocloses the file. Load data as a dict into extdata
with open('/home/grobot/code/datastore.json') as json_file:
    extdata = json.load(json_file)

# Setup Adafruit IO (Python ed.)
print("initializing Adafruit IO connection to user:", extdata["Adafruit_IO"][0]["AIO_USERNAME"])
lcddisplay('SETUP', 'ADA_IO CONN INIT', 'b')
try:
    aio_username = extdata["Adafruit_IO"][0]["AIO_USERNAME"]  # This returns username as setup in our json file.
    aio_key = extdata["Adafruit_IO"][0]["AIO_KEY"]
    aio = Client(aio_username, aio_key)
except:  # todo, find out what exceptions will actually be raised and specifically catch them
    print("UNABLE TO CONNECT TO ADAFRUIT IO; RELOADING")
    lcddisplay('ERROR', 'ADA_IO CONN FAIL', 'r')
    raise RuntimeError('ADA_IO_CONN_ERROR')

# Define Adafruit group name
groupKey = extdata["Enclosure"][0]["Serial"]  # enclosure serial number: GroBot-xxx-xxx
print("connecting to group: ", groupKey)
try:
    sensor_group = aio.groups(groupKey)
except RequestError:
    print('GROUP NOT FOUND; Please create one with a name exactly matching Serial in datastore.json. Format should be: grobot-xxx-xxx')
    lcddisplay('ERROR', 'ADA_IO GROUP ERR', 'r')
    raise RuntimeError('ADA_IO_GROUP_ERROR')
    # sensor_group = aio.create_group('grow-enclosure-'+sn,'Grow Enclosure Sensors')
    # Don't like auto-creation of new groups, instead return an error to go and make a group

print('connecting to sensor data feeds')
try:  # Each sensor should be defined as groupkey.sensor eg. GroBot-xxx-xxx.temperature
    tempFeed = aio.feeds(groupKey+'.temperature')
    rhFeed = aio.feeds(groupKey+'.humidity')
    smsFeed = aio.feeds(groupKey+'.soil-moisture')
except RequestError:
    print("FEEDS NOT FOUND. Please create 3 data feeds exactly named Temperature, Humidity, and Soil Moisture")
    lcddisplay('ERROR', 'ADA_IO FEED ERR', 'r')
    raise RuntimeError('ADA_IO_SENSOR_FEED_ERROR')
    # tempFeed = aio.create_data(groupKey,'temperature')
    # rhFeed = aio.create_data(groupKey,'humidity')
    # smsFeed = aio.create_data(groupKey,'soil-moisture')
    # do not like code making feeds by itself instead return error to go and make feeds

# Main Functions
async def updateSensorData(updateRate=1):
    # update rate in updates / min
    updateDelay = 60/updateRate

    while True:
        # read sensors
        temp = ths.temperature
        rh = ths.relative_humidity
        moist = sms.moisture_read()

        t = time.localtime(time.time())
        print("Time:", t[3:6], "Temp(C)=", temp, "%RH=", rh, "Soil Moisture=", moist)
        normal_sys_time = str(time.strftime('%H:%M', t))
        normal_sys_string = str('T:')+str(int(temp))+str(' RH:')+str(int(rh))+str(' M:')+str(int(moist))
        lcddisplay('NORMAL Clk '+normal_sys_time, normal_sys_string, 'g')

        # send data to dashboard
        aio.send_data(tempFeed.key, temp)
        aio.send_data(rhFeed.key, rh)
        aio.send_data(smsFeed.key, moist)

        await asyncio.sleep(updateDelay)
        continue
    return

async def buttonControl():
    while True:
        # special code to force a reset if screen goes crazy
        if lcd.select_button:
            raise RuntimeError('SCREEN_SELF_RESET')
        else:
            pass
        pump.buttonInput()
        light.buttonInput()
        fan.buttonInput()
        await asyncio.sleep(0.5)
        continue
    return

async def climateControl(plant, rate=6):
    rateDelay = 60/rate
    while True:
        t_now = time.time()  # already in unix format
        t_check = hhmm2unixToday(plant.checkTime)
        t_sunrise = hhmm2unixToday(plant.sunrise)
        t_sunset = hhmm2unixToday(plant.sunset)

        temp = ths.temperature
        rh = ths.relative_humidity

        # Read the soil moisture and water once per day
        if abs(t_now - t_check) <= rateDelay:
            print("CHECKING SOIL MOISTURE")
            lcddisplay('CHECKING', 'SOIL MOIST CHECK', 'b')
            moist = sms.moisture_read()
            if moist <= plant.dryValue:
                print("SOIL TOO DRY")
                lcddisplay('CHECKING', 'SOIL IS DRY', 'b')
                autoWater(plant.waterVol, pump)
        else:
            pump.circuit.value = False
            pump.default = False

        # light on at 'sunrise' and off at 'sunset'
        if (t_sunrise <= t_now) and (t_sunset >= t_now):
            light.circuit.value = True
            light.default = True
        else:
            light.circuit.value = False
            light.default = False

        # turn on fan if temp or humidity is too high
        if (temp >= plant.maxTemp) or (rh >= plant.maxHumid):
            fan.circuit.value = True
            fan.default = True
        else:
            fan.circuit.value = False
            fan.default = False

        await asyncio.sleep(rateDelay)
        continue
    return

def autoWater(V_water, P=pump):
    t_water = int(V_water / P.flowRate)  # how long to run the pump to achieve desired water vol.
    t_start = time.time()
    while time.time() <= (t_start+t_water):
        P.circuit.value = True
        time.sleep(1)
        I_pump = cs.current
        if False:  # I_pump >= P.minCurrent: #run dry detection disabled pending further testing
            # warnLED.value = True
            print("WARNING: PUMP RUNNING DRY")
            print("Pump Current = ", I_pump, " mA")
            lcddisplay('WARNING', 'RESERVOIR DRY', 'r')
        else:
            # warnLED.value = False
            print("AUTOWATERING IN PROGRESS")
            print("Pump Current = ", I_pump, " mA")
            lcddisplay('NORMAL', 'WATERING', 'g')
    P.circuit.value = False
    print("AUTOWATERING COMPLETE")
    lcddisplay('NORMAL', 'WATERING DONE', 'g')

    return

def hhmm2unixToday(t):
    '''
    converts a tuple of t=(hh, mm) to the unix int
    of that time today
    '''
    assert type(t) == tuple
    assert len(t) == 2
    assert (type(t[0]) == int) and (type(t[1]) == int)
    t_unix = time.localtime(time.time())
    t_unix = time.mktime((
        t_unix.tm_year,
        t_unix.tm_mon,
        t_unix.tm_mday,
        t[0],
        t[1],
        0,
        t_unix.tm_wday,
        t_unix.tm_yday,
        t_unix.tm_isdst,
    ))
    return t_unix

# Main loop
print("setup complete")
lcddisplay('SETUP', 'SETUP DONE', 'b')

async def main():
    # Display main menu
    main_menu()

    updateSensorTask = asyncio.create_task(updateSensorData())
    buttonControlTask = asyncio.create_task(buttonControl())
    climateControlTask = asyncio.create_task(climateControl(plant))

    await asyncio.gather(
        updateSensorTask,
        buttonControlTask,
        climateControlTask
    )

try:
    asyncio.run(main())
except MemoryError:
    print("MEMORY ERROR; RELOADING")
    lcddisplay('ERROR', 'MEM ERR', 'r')
    raise RuntimeError('MEMORY_ERROR')
except:
    print("UNHANDLED EXCEPTION; RELOADING")
    lcddisplay('ERROR', 'PC LOAD LETTER', 'r')
    for s in [s1, s2, s3, s4, s5]:
        s.direction = digitalio.Direction.OUTPUT
        s.drive_mode = digitalio.DriveMode.PUSH_PULL
        s.value = False
    raise RuntimeError('PC_LOAD_LETTER')
