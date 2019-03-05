from flask import Flask, request, jsonify, render_template, session
from monitor import Monitor
from validators import validate_monitor
import logging
from datastore import add_data, get_data
from functions import encrypt
from datetime import datetime

app = Flask(__name__)


@app.route('/api/test/mockup', methods=['POST', 'GET'])
def api_test_mockup():
    '''
    For dev purposes
    '''
    if request.method == 'POST':
        json_data = request.get_json(silent=True)
        if json_data['username'] != 'username' or json_data['password'] != 'password':
            return jsonify({'error': 'Invalid login'}), 401
        return jsonify({
            'token': '123'
        })
    return jsonify({'data': 'OK'})


@app.route('/api/test', methods=['POST'])
def api_test():
    try:
        json_data = validate_monitor(request.get_json(silent=True))
    except Exception as err:
        logging.error(str(err))
        return jsonify({'error': str(err)}), 400

    monitor = Monitor(**json_data, plain_txt_pw=True)
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


@app.route('/api/monitors')
@app.route('/api/monitors/<string:monitor_name>')
def api_get_monitors(monitor_name=None):
    data = get_data(monitor_name=monitor_name)
    status_code = 200 if data else 404
    return jsonify(data), status_code


@app.route('/')
def view_index():
    data = get_data()
    return render_template('index.html', monitors=data)


@app.route('/add-monitor')
def view_add_monitor():
    return render_template('monitor_form.html')


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
