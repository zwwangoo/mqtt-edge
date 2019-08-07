from flask import Flask, request

from extensions import socketio, bootstrap
from views import bp
from edge_client import EdgeClient
from tests.cloud_client import CloudClient
from config import config
from flask_socketio import emit, send

edge = None
cloud = CloudClient(config.HOST, config.PORT)


def create_app():

    app = Flask(__name__)

    app.config['SECRET'] = 'my secret key'
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['MQTT_BROKER_URL'] = '127.0.0.1'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_USERNAME'] = 'admin'
    app.config['MQTT_PASSWORD'] = 'password'
    app.config['MQTT_KEEPALIVE'] = 5
    app.config['MQTT_TLS_ENABLED'] = False

    with app.app_context():
        socketio.init_app(app, async_mode=None)
    bootstrap.init_app(app)

    app.register_blueprint(bp)
    return app


@socketio.on('edge_client', namespace='/edge')
def handle_edge_client(client_id):
    global edge
    edge = EdgeClient(config.HOST, config.PORT, config.SQLITE_PATH, client_id)
    edge.client.user_data_set([socketio, request.sid])
    edge.connect()
    edge.loop_start()


@socketio.on('cloud_start', namespace='/edge')
def handle_cloud():
    cloud.connect()
    cloud.client.user_data_set([socketio, request.sid])
    cloud.loop_start()


@socketio.on('edge_register', namespace='/edge')
def handle_edge_register(register):
    rc, final_mid = edge.publish('video/cloudipcmgr/register')


@socketio.on('cloud_cmd', namespace='/edge')
def handle_cloud_cmd(term_sn):
    cloud.tr_stram_cmd(term_sn)


if __name__ == '__main__':
    app = create_app()
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=True, debug=True)
