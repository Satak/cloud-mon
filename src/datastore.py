from datetime import datetime
from google.cloud import datastore
from conf import NAMESPACE, KIND
import logging

client = datastore.Client(namespace=NAMESPACE)


def update_monitor_state(name, ok, last_check, kind=KIND):
    try:
        record = get_data(monitor_name=name, kind=kind)
        if not record:
            err_msg = f'Record {name} not found while trying to update monitoring data'
            logging.error(err_msg)
            return {'error': err_msg, 'status_code': 404}
        with client.transaction():
            record['ok'] = ok
            record['last_check'] = last_check
            client.put(record)
    except Exception as err:
        logging.error(f'Error exception while trying to update monitorg data for {name}: {err}')


def add_data(data, kind=KIND):
    record = get_data(monitor_name=data['name'], kind=kind)
    if record:
        return {'error': f'Record {record["name"]} already exists', 'status_code': 400}
    try:
        with client.transaction():
            item = datastore.Entity(key=client.key(kind, data['name']))
            item.update(data)
            client.put(item)
        return {'data': dict(item), 'status_code': 201}
    except Exception as err:
        return {'error': str(err), 'status_code': 400}


def modify_data(data, kind=KIND):
    modify_fields = (
        'base_url',
        'monitor_path',
        'login_path',
        'username',
        'password',
        'enabled'
    )
    record = get_data(monitor_name=data['name'], kind=kind)
    if not record:
        return {'error': f'Record {data["name"]} not found', 'status_code': 404}
    try:
        with client.transaction():
            for prop in record:
                value = record[prop]
                data_value = data.get(prop)
                if data_value is not None and prop in modify_fields and data_value != value:
                    logging.info(f'Changing value for {data["name"]} prop: {prop}')
                    record[prop] = data_value
            client.put(record)
        return {'data': dict(record), 'status_code': 200}
    except Exception as err:
        err_message = f'Error while modifying {record["name"]}. Error: {err}'
        logging.error(err_message)
        return {'error': err_message, 'status_code': 400}


def get_data(monitor_name=None, kind=KIND):
    if monitor_name:
        key = client.key(kind, monitor_name)
        return client.get(key=key)
    return [item for item in client.query(kind=kind).fetch() if item]


def delete_data(monitor_name, kind=KIND):
    try:
        item = client.key(kind, monitor_name)
        client.delete(item)
        return {'data': {}, 'status_code': 204}
    except Exception as err:
        return {'error': str(err), 'status_code': 400}
