import logging
import requests
from conf import DECRYPTION_KEY, DECRYPTION_URL, TIMEOUT
from datetime import datetime


class Monitor:
    def __init__(self, name, base_url, login_path, monitor_path, username, password, timestamp=None, plain_txt_pw=False):
        self.name = name
        self.base_url = base_url
        self.login_path = login_path
        self.monitor_path = monitor_path
        self.username = username
        self.password = password if plain_txt_pw else self._decrypt_password(password)
        self.timestamp = timestamp if timestamp else datetime.utcnow()
        self.token = self._login()
        self.ok = False
        self.status_code = None

    @property
    def _headers(self):
        return {
            'Authorization': f'Bearer {self.token}'
        }

    @property
    def _credentials(self):
        return {
            'username': self.username,
            'password': self.password
        }

    @property
    def _monitor_url(self):
        return self.base_url + self.monitor_path

    @property
    def _login_url(self):
        return self.base_url + self.login_path

    @property
    def _state_str(self):
        return 'OK' if self.ok else 'ERROR'

    def _decrypt_password(self, encrypted_password):
        data = {
            'action': 'decrypt',
            'key': DECRYPTION_KEY,
            'data': encrypted_password
        }
        try:
            return requests.post(DECRYPTION_URL, json=data, timeout=TIMEOUT).json()['data']
        except Exception as err:
            logging.error(f'Decryption failed for {self.name}, {err}')

    def _login(self):
        try:
            return requests.post(self._login_url, json=self._credentials, timeout=TIMEOUT).json()['token']
        except Exception as err:
            logging.error(f'Error {self.name} while trying to login: {err}')

    def monitor(self):
        if not self.token:
            logging.error(f'No token for {self.name}')
            return None
        try:
            r = requests.get(self._monitor_url, headers=self._headers, timeout=TIMEOUT)
            self.ok = r.ok
            self.status_code = r.status_code
        except Exception as err:
            logging.error(f'Monitoring failed for {self.name}, {err}')

    def as_dict(self):
        return {
            'name': self.name,
            'baseUrl': self.base_url,
            'ok': self.ok,
            'statusCode': self.status_code,
            'timestamp': str(self.timestamp)
        }

    def __repr__(self):
        return f'{self.name} {self._state_str}'

    def __str__(self):
        return f'{self.name} {self._state_str}'
