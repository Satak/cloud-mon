import yaml
from conf import CONF_FILE
from monitor import Monitor
from datetime import datetime


def load_conf_file(file_name):
    with open(file_name) as file:
        return yaml.load(file)


def main():
    # same datetime for all monitors
    now = datetime.utcnow()
    data = load_conf_file(CONF_FILE)
    monitors = [Monitor(**value, timestamp=now) for key, value in data['monitors'].items()]
    for monitor in monitors:
        monitor.monitor()
        print(monitor.as_dict())


if __name__ == '__main__':
    main()
