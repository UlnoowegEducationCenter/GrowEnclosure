#Growth Enclosure additional Python code
#Ulnooweg Education Centre - All rights reserved
#Contact: ulnoowegeducation.ca

#NOTES: This file define the plant class as an input for main.py
########################################

class PlantDef:
    def __init__(self, name, dryValue, maxTemp, maxHumid, waterVol, checkTime, sunrise, sunset):
        self.name       = name # string of plants name
        self.dryValue   = dryValue # dry threashold for autowatering to kick in
        self.maxTemp    = maxTemp # warm threashold for turning on the ventillation fan
        self.maxHumid   = maxHumid # RH threashold for turning on the ventillation fan
        self.waterVol   = waterVol # ammount of water added during autowatering [mL]
        self.checkTime  = checkTime # time that the soil moisture is checked (hh,mm)
        self.sunrise    = sunrise # time that the grow light turns on (hh,mm)
        self.sunset     = sunset # time that the grow light turns off (hh,mm

#########################################################

testPlant = PlantDef(
    name      = 'testPlant',
    dryValue  = 800, # 100
    maxTemp   = 30, #up by 1 
    maxHumid  = 90, #5 % 
    waterVol  = 600, #10
    checkTime = (12,00), # use 24h time!
    sunrise   = (7,00), #Cannot use 07 - leading zeroes not permitted
    sunset    = (19,00)
    )
