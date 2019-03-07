import logging
from flask import Flask, request, jsonify, render_template, abort
from flask_basicauth import BasicAuth
from monitor import Monitor
from validators import validate_monitor
from datastore import add_data, get_data, delete_data, modify_data
from functions import encrypt, monitor_all
from datetime import datetime
from conf import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD

basic_auth = BasicAuth(app)
logging.getLogger().setLevel(logging.INFO)


# API
@app.route('/api/test', methods=['POST'])
@basic_auth.required
def api_test():
    try:
        json_data = validate_monitor(request.get_json(silent=True))
    except Exception as err:
        logging.error(str(err))
        return jsonify({'error': str(err)}), 400

    monitor = Monitor(**json_data)
    monitor.monitor()
    return jsonify({'success': monitor.ok})


@app.route('/api/monitors', methods=['POST'])
@basic_auth.required
def api_add_monitor():
    try:
        json_data = validate_monitor(request.get_json(silent=True))
    except Exception as err:
        logging.error(str(err))
        return jsonify({'error': str(err)}), 400

    json_data['password'] = encrypt(json_data['password'])
    json_data['created'] = datetime.utcnow()
    json_data['last_check'] = None
    json_data['ok'] = None
    data = add_data(json_data)
    return jsonify(data), data['status_code']


@app.route('/api/monitors/<string:monitor_name>', methods=['PUT'])
@basic_auth.required
def api_edit_monitor(monitor_name):
    try:
        json_data = validate_monitor(request.get_json(silent=True))
    except Exception as err:
        logging.error(str(err))
        return jsonify({'error': str(err)}), 400

    password = json_data['password']
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
            del item['password']
            data.append(item)
    else:
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
    del monitor['password']
    return render_template('monitor_form.html', monitor=monitor, action='edit')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
