from flask import Blueprint, request, Response
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError

from extensions import db
from clients.cloud_client import CloudClient
from utils.sql_utils import fetchone
from utils.data_utils import str_to_dict
from logger import log

cloud_bp = Blueprint('cloud', __name__, url_prefix='/cloud')

CLOUD = {}


@cloud_bp.route('/client', methods=['GET', 'DELETE'])
def cloud_server():
    client = CLOUD.get('cloud')
    if request.method == 'GET':
        user = request.form.get('user', 'admin')
        password = request.form.get('password', 'password')
        if not client:
            config = fetchone(
                '''
                select
                    broker_host host,
                    broker_port port,
                    sqlite_path SQLITE_PATH
                from config
                ''')
            if not config:
                return 'error, Not configured'
            client = CloudClient(config.HOST, config.PORT)
            CLOUD['cloud'] = client
        if not client.connected:
            client.connect(user, password)
            client.loop_start()
        return 'cloud connected'
    else:
        client.disconnect()
        return 'cloud disconnect'


@cloud_bp.route('/term_sn', methods=['POST', 'PUT', 'DELETE', 'GET'])
def cloud_term_sn():
    term_sn = request.form.get('term_sn')
    term_config = request.form.get('config')

    term_config, rc = str_to_dict(term_config)
    if rc != 1:
        return 'term_config error'
    if request.method == 'GET':
        edge = fetchone(
            text('select term_sn, config from edge where term_sn=:term_sn'),
            {'term_sn': term_sn})
        return Response(edge.config)
    elif request.method == 'POST':
        sql = text(
            'insert into edge (term_sn, config) values (:term_sn, :config)')
        params = {'term_sn': term_sn, 'config': term_config}
    elif request.method == 'PUT':
        sql = text(
            'update edge set config=:config where term_sn=:term_sn'
        ),
        params = {'config': term_config, 'term_sn': term_sn}
    else:
        sql = text('delete from edge where term_sn=:term_sn')
        params = {'term_sn': term_sn}

    try:
        db.session.execute(sql, params)
        db.session.commit()
    except DatabaseError as e:
        log.error(e)
        return 'error'
    return 'ok'


@cloud_bp.route('/cmd', methods=['POST'])
def cloud_cmd():
    term_sn = request.form.get('term_sn')
    cloud = CLOUD.get('cloud')
    cloud.publish_cmd(term_sn)
    return 'cmd success'


@cloud_bp.route('/publish', methods=['POST'])
def cloud_publish():
    topic = request.form.get('topic')
    message = request.form.get('message')
    qos = int(request.form.get('qos'))
    client = CLOUD.get('cloud')

    data, rc = str_to_dict(message)
    if rc != 1:
        return 'message error'

    if client and client.connected:
        rc, mid = client.publish(topic, data, qos)
        if rc == 0:
            return 'publish succeeded.'
    return 'publish error.'
