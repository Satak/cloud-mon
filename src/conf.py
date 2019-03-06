from os import getenv, path

DECRYPTION_KEY = getenv('DECRYPTION_KEY')
DECRYPTION_URL = getenv('DECRYPTION_URL')
BASIC_AUTH_USERNAME = getenv('BASIC_AUTH_USERNAME')
BASIC_AUTH_PASSWORD = getenv('BASIC_AUTH_PASSWORD')
NAMESPACE = getenv('NAMESPACE')
CONF_FILE = path.join(path.dirname(__file__), '../data/data.yaml')
TIMEOUT = 20
