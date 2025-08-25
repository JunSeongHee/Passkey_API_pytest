import configparser, os
from pathlib import Path

util_dir = Path(__file__).resolve().parent
project_root = util_dir.parent
config_path = project_root / 'configuration' / 'config.ini'

config = configparser.RawConfigParser()
config.read(config_path, encoding='UTF8')

class readConfig:
    @staticmethod
    def getValue(section, key):
        return config.get(section, key)

