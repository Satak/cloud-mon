import logging
import requests
from conf import DECRYPTION_KEY, DECRYPTION_URL, TIMEOUT
from datetime import datetime


class Monitor:
    def __init__(
            self,
            name,
            enabled,
            base_url,
            monitor_type,
            login_path=None,
            monitor_path=None,
            username=None,
            password=None,
            created=None,
            last_check=None,
            ok=None,
            status_code=None,
            plain_pw=True):
        self.name = name
        self.enabled = enabled
        self.base_url = base_url
        self.monitor_type = monitor_type
        self.login_path = login_path
        self.monitor_path = monitor_path
        self.username = username
        self.password = self._encrypt_password(password) if plain_pw else password
        self.last_check = None
        self.created = created if created else datetime.utcnow()
        self.token = None
        self.ok = ok
        self.status_code = status_code
        self.response_time = None

    @property
    def _headers(self):
        if self.monitor_type == 'tokenAuth':
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
        return f'{self.base_url}{self.monitor_path}' if self.monitor_type == 'tokenAuth' else self.base_url

    @property
    def _login_url(self):
        return self.base_url + self.login_path

    @property
    def state_str(self):
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
        if self.monitor_type in ('basicAuth', 'tokenAuth'):
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
            self.token = requests.post(self._login_url, json=self._credentials, timeout=TIMEOUT).json()['token']
        except Exception as err:
            logging.error(f'Error {self.name} while trying to login: {err}')

    def monitor(self):
        monitor_datetime = datetime.utcnow()
        self.last_check = monitor_datetime
        if self.monitor_type == 'tokenAuth':
            self._login()
            if not self.token:
                logging.error(f'No token for {self.name}')
                self.ok = False
                self.status_code = None
                return None
        try:
            r = requests.get(self._monitor_url, headers=self._headers, timeout=TIMEOUT)
            self.response_time = int(1000 * (r.elapsed.total_seconds()))
            self.ok = r.ok
            self.status_code = r.status_code
        except Exception as err:
            self.ok = False
            self.status_code = None
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
            'last_check': self.last_check,
            'created': self.created,
            'password': self.password,
            'response_time': self.response_time
        }
        if not password:
            del dict_data['password']
        return dict_data

    def __repr__(self):
        return f'{self.name} {self.state_str}'

    def __str__(self):
        return f'{self.name} {self.state_str}'
