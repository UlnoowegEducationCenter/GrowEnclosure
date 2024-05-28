import configparser
from addclass import PlantDef

config = configparser.ConfigParser()

Plant = None

def load_plant_settings():
    global Plant, config
    config.read("grobot_cfg.ini")
    Plant = PlantDef(
        name="Configured Plant",
        dryValue=int(config['PLANTCFG']['dryValue']),
        maxTemp=int(config['PLANTCFG']['maxTemp']),
        maxHumid=int(config['PLANTCFG']['maxHumid']),
        waterVol=int(config['PLANTCFG']['waterVol']),
        checkTime=tuple(int(x) for x in config['PLANTCFG']['checkTime'].split(",")),
        sunrise=tuple(int(x) for x in config['PLANTCFG']['sunrise'].split(",")),
        sunset=tuple(int(x) for x in config['PLANTCFG']['sunset'].split(",")),
        fanTime=int(config['PLANTCFG']['fanTime'])
    )

def save_plant_settings():
    global Plant, config
    config['PLANTCFG']['dryValue'] = str(Plant.dryValue)
    config['PLANTCFG']['maxTemp'] = str(Plant.maxTemp)
    config['PLANTCFG']['maxHumid'] = str(Plant.maxHumid)
    config['PLANTCFG']['waterVol'] = str(Plant.waterVol)
    config['PLANTCFG']['checkTime'] = ",".join(map(str, Plant.checkTime))
    config['PLANTCFG']['sunrise'] = ",".join(map(str, Plant.sunrise))
    config['PLANTCFG']['sunset'] = ",".join(map(str, Plant.sunset))
    config['PLANTCFG']['fanTime'] = str(Plant.fanTime)
    with open("grobot_cfg.ini", "w") as configfile:
        config.write(configfile)
