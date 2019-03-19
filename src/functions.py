import logging
from datetime import datetime
import smtplib
from email.message import EmailMessage
import requests
from conf import (
    DECRYPTION_KEY,
    DECRYPTION_URL,
    TIMEOUT,
    SENDER_EMAIL,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    SMTP_SERVER,
    TO_EMAIL,
    SEND_EMAIL
)
from monitor import Monitor
from datastore import get_data, update_monitor_state


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


def send_email(subject, message, sender, recipients, smtp_server, smtp_username, smtp_password, smtp_port=465):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipients
    msg.set_content(message)
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
            logging.info(f'Email sent to {recipients}')
    except Exception as err:
        logging.error(f'Error while trying to send email to {recipients}, error: {err}')


def monitor_all():
    data = get_data()
    monitors = [Monitor(**item, plain_pw=False) for item in data if item.get('enabled')]
    for monitor in monitors:
        last_state = monitor.state_str
        monitor.monitor()
        if monitor.state_str != last_state:
            message = f'{monitor.name} monitor state changed from {last_state} -> {monitor.state_str}'
            subject = f'MONITOR {monitor.name} {monitor.state_str}'
            if SEND_EMAIL:
                email_conf = {
                    'subject': subject,
                    'message': message,
                    'sender': SENDER_EMAIL,
                    'recipients': TO_EMAIL.split(','),
                    'smtp_server': SMTP_SERVER,
                    'smtp_username': SMTP_USERNAME,
                    'smtp_password': SMTP_PASSWORD
                }
                send_email(**email_conf)
            logging.info(message)
        update_monitor_state(monitor.name, monitor.ok, monitor.last_check, monitor.response_time)
    return {'data': 'monitoring done'}
