import logging
import yaml
import requests
from conf import CONF_FILE, DECRYPTION_KEY, DECRYPTION_URL, TIMEOUT
from monitor import Monitor
from datetime import datetime
from datastore import get_data
from pprint import pprint
from datastore import update_monitor_data


def load_conf_file(file_name):
    with open(file_name) as file:
        return yaml.load(file)


def monitor_all():
    # same last_check for all monitors
    now = datetime.utcnow()
    data = get_data()
    monitors = [Monitor(**item, last_check=now) for item in data if item.get('enabled')]
    for monitor in monitors:
        monitor.monitor()
        update_monitor_data(monitor.as_dict(password=True))
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
        logging.error(f'Encryption failed: {err}')
