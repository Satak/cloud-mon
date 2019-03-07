import logging
import smtplib
import yaml
import requests
from conf import (
    CONF_FILE,
    DECRYPTION_KEY,
    DECRYPTION_URL,
    TIMEOUT,
    SENDER_EMAIL,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_SERVER,
    TO_EMAIL
)
from monitor import Monitor
from datetime import datetime
from datastore import get_data
from pprint import pprint
from datastore import update_monitor_data


def load_conf_file(file_name):
    with open(file_name) as file:
        return yaml.load(file)


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


def send_email(subject, body, to_email, smtp_port=587):
    with smtplib.SMTP(SMTP_SERVER, smtp_port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(SENDER_EMAIL, to_email, msg)
        logging.info(f'Email sent to {to_email}')


def monitor_all():
    # same last_check for all monitors
    # now = datetime.utcnow
    data = get_data()
    monitors = [Monitor(**item, plain_pw=False) for item in data if item.get('enabled')]
    for monitor in monitors:
        last_state = monitor.state_str
        monitor.monitor()
        if monitor.state_str != last_state:
            body = f'{monitor.name} monitor state changed from {last_state} -> {monitor.state_str}'
            subject = f'MONITOR {monitor.name} {monitor.state_str}'
            send_email(subject, body, TO_EMAIL)
            logging.info(body)
        update_monitor_data(monitor.as_dict(password=True, date_as_str=False))
    return {'data': 'monitoring done'}
