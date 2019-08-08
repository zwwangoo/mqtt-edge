from flask import Blueprint, render_template, request
from clients.edge_client import EdgeClient
from utils.data_utils import get_utctime

from config import config

edge_bp = Blueprint('edge', __name__, url_prefix='/edge')

EDGESALL = {}


@edge_bp.route('/term_sn', methods=['GET', 'POST'])
def edge():

    term_sn = request.form.get('term_sn')
    client = EDGESALL.get(term_sn, None)
    if request.method == 'GET':
        if client and client.connected:
            return '%s' % term_sn
        else:
            return '%s does not exist' % term_sn
    else:
        user = request.form.get('user', 'admin')
        password = request.form.get('password', 'password')
        term_config = request.form.get('term_config')

        if not client:
            client = EdgeClient(config.HOST, config.PORT,
                                term_sn=term_sn,
                                sqlite_path=config.SQLITE_PATH,
                                config=term_config)
            EDGESALL[term_sn] = client

        if not client.connected:
            client.connect(user, password)
            client.loop_start()
        return '%s connected' % term_sn


@edge_bp.route('/register', methods=['POST'])
def edge_register():
    term_sn = request.form.get('term_sn')
    client = EDGESALL.get(term_sn)
    if not client:
        return '%s dose not exist.'
    client.publish_register()
    return 'successed.'


@edge_bp.route('/report', methods=['POST'])
def edge_report():
    term_sn = request.form.get('term_sn')
    client = EDGESALL.get(term_sn)
    if client and client.connected:
        client.publish_report(data={
            "time": get_utctime(),
            "term_sn": term_sn,
            "data": {
                "type": "motion",
                "event": "start",
                "timestamp": 1564140943,
            },
            "type": "ai_event",
            "cmd": "report"
        })
    return 'report ok'
