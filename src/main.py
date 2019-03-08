import logging
from flask import Flask, request, jsonify, render_template, abort
from flask_basicauth import BasicAuth
from monitor import Monitor
from validators import token_auth_validate, basic_auth_validate, no_auth_validate
from datastore import add_data, get_data, delete_data, modify_data
from functions import encrypt, monitor_all
from datetime import datetime
from conf import (
    BASIC_AUTH_USERNAME,
    BASIC_AUTH_PASSWORD,
    SEND_EMAIL,
    TIMEOUT,
    SENDER_EMAIL,
    SMTP_SERVER,
    TO_EMAIL,
    SENDER_EMAIL,
    NAMESPACE
)

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD

basic_auth = BasicAuth(app)
logging.getLogger().setLevel(logging.INFO)


def validate_payload(payload):
    monitor_type = payload['monitor_type']
    validate_map = {
        'noAuth': lambda data: no_auth_validate(data),
        'basicAuth': lambda data: basic_auth_validate(data),
        'tokenAuth': lambda data: token_auth_validate(data)
    }
    try:
        return validate_map[monitor_type](payload)
    except Exception as err:
        logging.error(str(err))
        return {'error': str(err)}


# API
@app.route('/api/test', methods=['POST'])
@basic_auth.required
def api_test():
    payload = request.get_json(silent=True)
    json_data = validate_payload(payload)
    if json_data.get('error'):
        return jsonify(json_data), 400

    monitor = Monitor(**json_data)
    monitor.monitor()
    return jsonify({'success': monitor.ok})


@app.route('/api/monitors', methods=['POST'])
@basic_auth.required
def api_add_monitor():
    payload = request.get_json(silent=True)
    json_data = validate_payload(payload)
    if json_data.get('error'):
        return jsonify(json_data), 400

    if json_data.get('password'):
        json_data['password'] = encrypt(json_data['password'])
    json_data['created'] = datetime.utcnow()
    json_data['last_check'] = None
    json_data['ok'] = None
    data = add_data(json_data)
    return jsonify(data), data['status_code']


@app.route('/api/monitors/<string:monitor_name>', methods=['PUT'])
@basic_auth.required
def api_edit_monitor(monitor_name):
    payload = request.get_json(silent=True)
    json_data = validate_payload(payload)
    if json_data.get('error'):
        return jsonify(json_data), 400

    password = json_data.get('password')
    monitor_type = json_data.get('monitor_type')
    if monitor_type in ('basicAuth', 'tokenAuth') and password:
        # modify_data will skip all None values!
        password = encrypt(password) if password else None
        json_data['password'] = password
    data = modify_data(json_data)
    return jsonify(data), data['status_code']


@app.route('/api/monitors')
@app.route('/api/monitors/<string:monitor_name>')
@basic_auth.required
def api_get_monitors(monitor_name=None):
    raw_data = get_data(monitor_name=monitor_name)
    if not raw_data:
        return jsonify({'error': 'No data'}), 404
    # NOTE: This is ugly!
    if isinstance(raw_data, list):
        data = []
        for item in raw_data:
            if 'password' in item:
                del item['password']
            data.append(item)
    else:
        if 'password' in raw_data:
            del raw_data['password']
        data = raw_data
    return jsonify(data)


@app.route('/api/monitors/<string:monitor_name>', methods=['DELETE'])
@basic_auth.required
def api_delete_monitor(monitor_name):
    data = delete_data(monitor_name)
    return jsonify(data), data['status_code']


@app.route('/api/invoke-monitor')
def api_invoke_monitor():
    from_app_engine = request.headers.get('X-Appengine-Cron')
    client_ip = request.remote_addr
    if not from_app_engine or client_ip != '127.0.0.1':
        logging.error(f'Invalid cron attempt! IP: {client_ip}')
        return abort(401)
    data = monitor_all()
    logging.info('Monitoring done')
    return jsonify(data)


@app.route('/api/ui-invoke-monitor', methods=['PUT'])
@basic_auth.required
def api_ui_invoke_monitor():
    data = monitor_all()
    logging.info('Monitoring done launched from UI')
    return jsonify(data)


@app.route('/api/status')
def api_status():
    logging.info('Status check')
    return jsonify({'status': 'OK'})


# Views
@app.route('/')
@basic_auth.required
def view_index():
    data = get_data()
    return render_template('index.html', monitors=data)


@app.route('/add-monitor')
@basic_auth.required
def view_add_monitor():
    return render_template('monitor_form.html', monitor=None, action='add')


@app.route('/monitors/<string:monitor_name>')
@basic_auth.required
def view_modify_monitor(monitor_name):
    monitor = get_data(monitor_name=monitor_name)
    if 'password' in monitor:
        del monitor['password']
    return render_template('monitor_form.html', monitor=monitor, action='edit')


@app.route('/settings')
@basic_auth.required
def view_settings():
    settings = {
        'namespace': NAMESPACE,
        'sender_email': SENDER_EMAIL,
        'smtp_server': SMTP_SERVER,
        'to_email': TO_EMAIL,
        'timeout': TIMEOUT,
        'send_email': SEND_EMAIL
    }
    return render_template('settings.html', settings=settings)


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
