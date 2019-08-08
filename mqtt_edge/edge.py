from flask import Blueprint, render_template, request
from edge_client import EdgeClient
from reports.report_ai_event import EdgeAIEvent

from config import config

edge_bp = Blueprint('edge', __name__, url_prefix='/edge')

EDGEALL = {}


@edge_bp.route('/')
def index():
    return render_template('edge.html')


@edge_bp.route('/term_sn', methods=['GET', 'POST'])
def edge():

    term_sn = request.form.get('term_sn')
    client = EDGEALL.get(term_sn, None)
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
            EDGEALL[term_sn] = client

        if not client.connected:
            client.connect(user, password)
            client.loop_start()
        return '%s connected' % term_sn


@edge_bp.route('/register', methods=['POST'])
def edge_register():
    term_sn = request.form.get('term_sn')
    client = EDGEALL.get(term_sn)
    if not client:
        return '%s dose not exist.'
    print(EDGEALL)

    client.publish('video/cloudipcmgr/register')
    return 'successed.'


@edge_bp.route('/report', methods=['POST'])
def edge_cloud_report():
    term_sn = request.form.get('term_sn')
    client = EdgeAIEvent(config.HOST, config.PORT,
                         term_sn=term_sn,
                         sqlite_path=config.SQLITE_PATH)
    client.connect()
    client.publish()
    return 'report ok'
