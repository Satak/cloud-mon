from datetime import datetime
from google.cloud import datastore
from conf import NAMESPACE


client = datastore.Client(namespace=NAMESPACE)


def add_data(data, kind='monitor'):
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


def get_data(monitor_name=None, kind='monitor'):
    if monitor_name:
        key = client.key(kind, monitor_name)
        item = client.get(key=key)
        return dict(item) if item else None
    return [dict(item) for item in client.query(kind=kind).fetch() if item]


def delete_data(monitor_name, kind='monitor'):
    try:
        item = client.key(kind, monitor_name)
        client.delete(item)
        return {'data': {}, 'status_code': 204}
    except Exception as err:
        return {'error': str(err), 'status_code': 400}
