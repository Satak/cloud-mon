from os import getenv, path
import base64

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
SEND_EMAIL = True

FIREBASE_CONFIG = {
    "apiKey": getenv('FB_API_KEY'),
    "authDomain": getenv('FB_AUTH_DOMAIN'),
    "databaseURL": getenv('FB_DB_URL'),
    "projectId": getenv('FB_PROJECT_ID'),
    "storageBucket": getenv('FB_STORAGE_BUCKET'),
    "messagingSenderId": getenv('FB_MESSAGE_SENDER_ID')
}

SECRET = base64.b64decode(getenv('SECRET').encode())

FIREBASE_ADMIN_SDK_KEY = getenv('GOOGLE_APPLICATION_CREDENTIALS_FIREBASE')
