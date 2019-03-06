from flask import Flask, request, jsonify, render_template
from flask_basicauth import BasicAuth
from monitor import Monitor
from validators import validate_monitor
import logging
from datastore import add_data, get_data, delete_data, modify_data
from functions import encrypt, monitor_all
from datetime import datetime
from conf import BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = BASIC_AUTH_USERNAME
app.config['BASIC_AUTH_PASSWORD'] = BASIC_AUTH_PASSWORD
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)


# API
@app.route('/api/test', methods=['POST'])
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
def api_add_monitor():
    try:
        json_data = validate_monitor(request.get_json(silent=True))
    except Exception as err:
        logging.error(str(err))
        return jsonify({'error': str(err)}), 400

    json_data['password'] = encrypt(json_data['password'])
    json_data['created'] = datetime.utcnow()
    data = add_data(json_data)
    return jsonify(data), data['status_code']


@app.route('/api/monitors/<string:monitor_name>', methods=['PUT'])
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
def api_get_monitors(monitor_name=None):
    data = get_data(monitor_name=monitor_name)
    status_code = 200 if data else 404
    return jsonify(data), status_code


@app.route('/api/monitors/<string:monitor_name>', methods=['DELETE'])
def api_delete_monitor(monitor_name):
    data = delete_data(monitor_name)
    return jsonify(data), data['status_code']


@app.route('/api/invoke-monitor')
def api_invoke_monitor():
    data = monitor_all()
    return jsonify(data)


# Views
@app.route('/')
def view_index():
    data = get_data()
    return render_template('index.html', monitors=data)


@app.route('/add-monitor')
def view_add_monitor():
    return render_template('monitor_form.html', monitor=None, action='add')


@app.route('/monitors/<string:monitor_name>')
def view_modify_monitor(monitor_name):
    monitor = get_data(monitor_name=monitor_name)
    del monitor['password']
    return render_template('monitor_form.html', monitor=monitor, action='edit')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
