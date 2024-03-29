import json
from flask import Blueprint, request
from mqtt_clients.edge_client import EdgeClient
from utils.sql_utils import fetchone
from utils.data_utils import isdict

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

        if not isdict(term_config):
            return 'term_config error'
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
            print(config.HOST)
            client = EdgeClient(config.HOST, config.PORT,
                                term_sn=term_sn,
                                sqlite_path=config.SQLITE_PATH,
                                config=term_config)
            EDGESALL[term_sn] = client

        if not client.connected:
            client.connect(user, password)
            client.loop_start()
            # 启动之后，自动注册
            client.publish_register()
        return '%s connected' % term_sn


@edge_bp.route('/register', methods=['POST'])
def edge_register():
    term_sn = request.form.get('term_sn')
    client = EDGESALL.get(term_sn)
    if not client:
        return '%s dose not exist.'
    client.publish_register()
    return 'Succeeded.'


@edge_bp.route('/publish', methods=['POST'])
def edge_publish():
    term_sn = request.form.get('term_sn')
    topic = request.form.get('topic')
    message = request.form.get('message')
    qos = int(request.form.get('qos'))
    client = EDGESALL.get(term_sn)

    if not isdict(message):
        return 'message error'

    if client and client.connected:
        rc, mid = client.publish(topic, json.loads(message), qos)
        if rc == 0:
            return 'publish succeeded.'
    return 'publish error.'


@edge_bp.route('/zmq/nodes', methods=['GET'])
def edge_zmq_nodes():
    nodes = []
    for term_sn in EDGESALL:
        client = EDGESALL.get(term_sn)

        nodes.append(client.evmgr.ident)
        for node in client.peers.keys():
            nodes.append(node)
    return ','.join(nodes)


@edge_bp.route('/<term_sn>/zmq/send', methods=['POST'])
def edge_zmq_send(term_sn):
    from_node = request.form.get('from')
    to_node = request.form.get('to')
    msg = request.form.get('msg')
    client = EDGESALL.get(term_sn)
    fnode = client.peers.get(from_node)
    if not fnode:
        fnode = client.evmgr
    if to_node == client.evmgr.ident:
        fnode.send(msg)
    else:
        fnode.send(msg, to_node)
    return 'ok'
