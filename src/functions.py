import logging
import yaml
import requests
from conf import CONF_FILE, DECRYPTION_KEY, DECRYPTION_URL, TIMEOUT
from monitor import Monitor
from datetime import datetime
from datastore import get_data


def load_conf_file(file_name):
    with open(file_name) as file:
        return yaml.load(file)


def monitor_all():
    # same last_check for all monitors
    now = datetime.utcnow()
    data = get_data()
    monitors = [Monitor(**value, last_check=now) for key, value in data['monitors'].items() if key.get('enabled')]
    for monitor in monitors:
        monitor.monitor()
    return {'data': 'monitoring done'}


def encrypt(data):
    try:
        json_data = {
            'action': "encrypt", 
            'key': DECRYPTION_KEY,
            'data': data
        }
        return requests.post(DECRYPTION_URL, json=json_data, timeout=TIMEOUT).json()['data']
    except Exception as err:
        logging.error(str(err))
