# sensorfeed.py
# Ulnooweg Education Centre - ulnoowegeducation.ca
# Growth enclosure V1.0
# All rights reserved
#
# This function read sensor feeds
# This function executes without input and returns Temp, %RH, and soilRH to main in raw form
# returns single number 0 on failure
#
##############################################
# MODULE IMPORTS
from diopinsetup import diopinset

##############################################
# Handle the pins definition and sensor definition
diop = diopinset()

print(f"Debug: diopinset returned: {diop}")  # Debugging line

if isinstance(diop, tuple):
    s1, s2, s3, s4, s5, s6, b1, ths, sms = diop
else:
    raise RuntimeError('Failed to initialize pins and sensors')

def feedread():  # define feedread function
    try:
        T = ths.temperature
        RH = ths.relative_humidity
        SRH = sms.moisture_read()

        return T, RH, SRH  # return tuple of all values
    except Exception as e:
        print(f"Error reading sensor values: {e}")
        return 0
