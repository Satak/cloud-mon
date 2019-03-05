import logging
import requests
from conf import DECRYPTION_KEY, DECRYPTION_URL, TIMEOUT
from datetime import datetime


class Monitor:
    def __init__(self, name, enabled, base_url, login_path, monitor_path, username, password, created=None, last_check=None):
        self.name = name
        self.enabled = enabled
        self.base_url = base_url
        self.login_path = login_path
        self.monitor_path = monitor_path
        self.username = username
        self.password = self._encrypt_password(password)
        self.last_check = last_check if last_check else datetime.utcnow()
        self.created = created if created else datetime.utcnow()
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
            'password': self._decrypt_password(self.password)
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

    def _encrypt_password(self, plain_text_password):
        data = {
            'action': 'encrypt',
            'key': DECRYPTION_KEY,
            'data': plain_text_password
        }
        try:
            return requests.post(DECRYPTION_URL, json=data, timeout=TIMEOUT).json()['data']
        except Exception as err:
            logging.error(f'Encryption failed for {self.name}, {err}')

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

    def as_dict(self, password=False):
        dict_data = {
            'name': self.name,
            'enabled': self.enabled,
            'base_url': self.base_url,
            'login_path': self.login_path,
            'monitor_path': self.monitor_path,
            'username': self.username,
            'ok': self.ok,
            'status_code': self.status_code,
            'last_check': str(self.last_check),
            'created': str(self.created),
            'password': self.password
        }
        if not password:
            del dict_data['password']
        return dict_data

    def __repr__(self):
        return f'{self.name} {self._state_str}'

    def __str__(self):
        return f'{self.name} {self._state_str}'
