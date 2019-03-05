from os import getenv, path

DECRYPTION_KEY = getenv('DECRYPTION_KEY')
DECRYPTION_URL = getenv('DECRYPTION_URL')
CONF_FILE = path.join(path.dirname(__file__), '../data/data.yaml')
TIMEOUT = 20
