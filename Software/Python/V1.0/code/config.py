# config.py

import configparser

config = configparser.ConfigParser()

def read_config():
    config.read("grobot_cfg.ini")
    return config

def get_plant_settings():
    config.read("grobot_cfg.ini")
    settings = {
        'sunrise': [int(x) for x in config['PLANTCFG']['sunrise'].split(",")],
        'sunset': [int(x) for x in config['PLANTCFG']['sunset'].split(",")],
        'checkTime': [int(x) for x in config['PLANTCFG']['checkTime'].split(",")],
        'dryValue': int(config['PLANTCFG']['dryValue']),
        'maxTemp': int(config['PLANTCFG']['maxTemp']),
        'maxHumid': int(config['PLANTCFG']['maxHumid']),
        'waterVol': int(config['PLANTCFG']['waterVol']),
        'fanTime': int(config['PLANTCFG']['fanTime'])
    }
    return settings

def update_config(section, parameter, value):
    config.read("grobot_cfg.ini")
    config[section][parameter] = str(value)
    with open('grobot_cfg.ini', 'w') as configfile:
        config.write(configfile)
