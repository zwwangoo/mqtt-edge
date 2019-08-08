from flask import Blueprint, request, Response
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError

from extensions import db
from clients.cloud_client import CloudClient
from utils.sql_utils import fetchone
from logger import log
from config import config

cloud_bp = Blueprint('cloud', __name__, url_prefix='/cloud')

cloud = CloudClient(config.HOST, config.PORT)


@cloud_bp.route('/client', methods=['GET', 'DELETE'])
def cloud_server():
    if request.method == 'GET':
        user = request.form.get('user', 'admin')
        password = request.form.get('password', 'password')
        if not cloud.connected:
            cloud.connect(user, password)
            cloud.loop_start()
        return 'cloud connected'
    else:
        cloud.disconnect()
        return 'cloud disconnect'


@cloud_bp.route('/term_sn', methods=['POST', 'PUT', 'DELETE', 'GET'])
def cloud_term_sn():
    term_sn = request.form.get('term_sn')
    term_config = request.form.get('config')
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
    cloud.publish_cmd(term_sn)
    return 'cmd success'