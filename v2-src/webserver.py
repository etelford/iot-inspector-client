from flask import Flask
from flask_cors import CORS
import inspector
import threading
import utils
import server_config
import time


PORT = 46241


app = Flask(__name__)
cors = CORS(
    app,
    resources={r"/*": {"origins": server_config.BASE_URL}}
)


context = {
    'host_state': None,
    'quit': False
}


def start_thread():

    th = threading.Thread(target=_monitor_web_server)
    th.daemon = True
    th.start()


def _monitor_web_server():

    utils.restart_upon_crash(app.run, kwargs={'port': PORT})


def log_http_request(request_name):

    host_state = context['host_state']
    if host_state is not None:
        utils.log('[HTTP] request:', request_name)
        with host_state.lock:
            host_state.last_ui_contact_ts = time.time()


@app.route('/get_status_text', methods=['GET'])
def get_status_text():

    log_http_request('/get_status_text')

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            return host_state.status_text

    return ''


@app.route('/is_inspecting_traffic', methods=['GET'])
def is_inspecting_traffic():

    log_http_request('/is_inspecting_traffic')

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            return str(host_state.is_inspecting_traffic).lower()

    return 'false'


@app.route('/get_user_key', methods=['GET'])
def get_user_key():

    log_http_request('/get_user_key')

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            if host_state.user_key is not None:
                return host_state.user_key

    return ''


@app.route('/start_fast_arp_discovery', methods=['GET'])
def start_fast_arp_discovery():

    log_http_request('/start_fast_arp_discovery')

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.fast_arp_scan = True

    return 'OK'


@app.route('/start_inspecting_traffic', methods=['GET'])
def start_inspecting_traffic():

    log_http_request('/start_inspecting_traffic')

    inspector.enable_ip_forwarding()

    # Start inspecting
    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.is_inspecting_traffic = True

    return 'OK'


@app.route('/pause_inspecting_traffic', methods=['GET'])
def pause_inspecting_traffic():

    log_http_request('/pause_inspecting_traffic')

    inspector.disable_ip_forwarding()

    host_state = context['host_state']
    if host_state is not None:
        with host_state.lock:
            host_state.is_inspecting_traffic = False

    return 'OK'


@app.route('/exit', methods=['GET'])
def exit_inspector():

    log_http_request('/exit')

    inspector.disable_ip_forwarding()

    context['quit'] = True

    return 'OK'
