import configparser
import os

CONFIG_FILENAME = "config.ini"
config_vault = None

def _get_configure():
    global config_vault
    if config_vault is not None:
        return config_vault
    
    if not os.path.exists(CONFIG_FILENAME):
        raise Exception(" %s config file can not be found" % CONFIG_FILENAME)

    try:
        config_vault = configparser.ConfigParser()
        config_vault.read(CONFIG_FILENAME)
        return config_vault
    except:
        print("invalid configration!")
        raise Exception("invalid configration file")
    

def get_config():
    config = {}
    users_section = _get_configure()["main"]
    config["username"] = users_section["username"]
    config["apikey"] = users_section["apikey"]
    config["output_path"] = users_section["output_path"] 
    # for entry in users_section:
    #     config[entry] = users_section[entry]
    return config



