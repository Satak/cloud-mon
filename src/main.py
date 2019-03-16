import logging
from functools import wraps
import pyrebase
import firebase_admin
from firebase_admin import credentials, auth as admin_auth
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    abort,
    redirect,
    session,
    url_for
)
from monitor import Monitor
from validators import token_auth_validate, basic_auth_validate, no_auth_validate
from datastore import (
    add_data,
    get_data,
    delete_data,
    modify_data,
    get_monitoring_data
)
from functions import encrypt, monitor_all
from datetime import datetime
from conf import (
    SEND_EMAIL,
    TIMEOUT,
    SENDER_EMAIL,
    SMTP_SERVER,
    TO_EMAIL,
    SENDER_EMAIL,
    NAMESPACE,
    SECRET,
    FIREBASE_CONFIG,
    FIREBASE_ADMIN_SDK_KEY
)

app = Flask(__name__)

app.secret_key = SECRET
firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
firebase_admin_cred = credentials.Certificate(FIREBASE_ADMIN_SDK_KEY)
firebase_admin.initialize_app(firebase_admin_cred)

logging.getLogger().setLevel(logging.INFO)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('view_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


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


def change_password(email, uid, current_password, new_password):
    try:
        # validate current password
        _ = auth.sign_in_with_email_and_password(email, current_password)
        admin_auth.update_user(uid, password=new_password)
        return True
    except Exception as err:
        print('Invalid credentials', str(err))


def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        user_info = auth.get_account_info(user['idToken'])
        if user_info:
            email_ = user_info['users'][0]['email']
            uid = user_info['users'][0]['localId']
            user = {
                'email': email_,
                'uid': uid
            }
            session['user'] = user
            return user
    except Exception as err:
        print('Invalid credentials', str(err))


# API
@app.route('/api/test', methods=['POST'])
@login_required
def api_test():
    payload = request.get_json(silent=True)
    json_data = validate_payload(payload)
    if json_data.get('error'):
        return jsonify(json_data), 400

    monitor = Monitor(**json_data)
    monitor.monitor()
    return jsonify({'success': monitor.ok})


@app.route('/api/monitors', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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


@app.route('/api/monitor-data/<string:monitor_name>')
@login_required
def api_get_monitor_data(monitor_name):
    return jsonify(get_monitoring_data(monitor_name))


@app.route('/api/monitors/<string:monitor_name>', methods=['DELETE'])
@login_required
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
@login_required
def api_ui_invoke_monitor():
    data = monitor_all()
    logging.info('Monitoring done launched from UI')
    return jsonify(data)


@app.route('/api/status')
@login_required
def api_status():
    logging.info('Status check')
    return jsonify({'status': 'OK'})


@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    payload = request.get_json(silent=True)
    current_password = payload['currentPassword']
    new_password = payload['newPassword']
    email = session.get('user')['email']
    uid = session.get('user')['uid']

    res = change_password(email, uid, current_password, new_password)
    if not res:
        return jsonify({'error': 'Password change failed'}), 401
    return jsonify({'message': 'Password changed successfully'})


@app.route('/api/login', methods=['POST'])
def api_login():
    payload = request.get_json(silent=True)
    email = payload['email']
    password = payload['password']
    user = login(email, password)
    if not user:
        return jsonify({'error': 'Invalid login'}), 401
    return jsonify({'message': 'Login success'})


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    if not session.get('user'):
        return jsonify({'error': 'Not logged in'}), 401
    del session['user']
    return jsonify({'message': 'Logout success'})


# Views
@app.route('/')
def view_login():
    if session.get('user'):
        return redirect(url_for('view_home'))
    return render_template('login.html')


@app.route('/home')
@login_required
def view_home():
    data = get_data()
    return render_template('home.html', monitors=data)


@app.route('/add-monitor')
@login_required
def view_add_monitor():
    return render_template('monitor_form.html', monitor=None, action='add')


@app.route('/account')
@login_required
def view_account():
    return render_template('account.html', email=session.get('user')['email'])


@app.route('/monitors/<string:monitor_name>')
@login_required
def view_modify_monitor(monitor_name):
    monitor = get_data(monitor_name=monitor_name)
    if 'password' in monitor:
        del monitor['password']
    return render_template('monitor_form.html', monitor=monitor, action='edit')


@app.route('/settings')
@login_required
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
