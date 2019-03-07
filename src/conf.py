from os import getenv, path

DECRYPTION_KEY = getenv('DECRYPTION_KEY')
DECRYPTION_URL = getenv('DECRYPTION_URL')
BASIC_AUTH_USERNAME = getenv('BASIC_AUTH_USERNAME')
BASIC_AUTH_PASSWORD = getenv('BASIC_AUTH_PASSWORD')
NAMESPACE = getenv('NAMESPACE')
SENDER_EMAIL = getenv('SENDER_EMAIL')
SMTP_USERNAME = getenv('SMTP_USERNAME')
SMTP_PASSWORD = getenv('SMTP_PASSWORD')
SMTP_SERVER = getenv('SMTP_SERVER')
TO_EMAIL = getenv('TO_EMAIL')
TIMEOUT = 20
KIND = 'monitor'
