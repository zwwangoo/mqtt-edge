'''
模拟云端的client
'''
import json
import time

from paho.mqtt.client import Client
from utils.data_utils import generate_md5, ordered_dict, get_utctime

from logger import log
# from extensions import socketio
from flask_socketio import emit

config = {
    "ml": [{
        "features": [1, 2, 3],
        "ip": "192.168.1.3",
        "ipcs": ["192.168.1.100", "192.168.1.111"]
    }],
    "pusher": [{
        "ip": "192.168.1.2",
        "ipcs": ["192.168.1.110", "192.168.1.111"],
        "status": [1, 0]
    }]
}


class CloudClient:
    def __init__(self, host, port, keepalive=60):

        self.client = Client(client_id='cloud', clean_session=False)

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self, user='admin', password='password'):
        self.client.username_pw_set(user, password)
        try:
            self.client.connect(self.host, self.port, self.keepalive)

            emit('cloud_log', {'data': 'cloud connected'})
        except ConnectionRefusedError as e:
            log.error(e)
            log.info('Retry after 1 second.')

            emit('cloud_log', {
                 'data': 'ConnectionResetError, Retry after 1 second.'})
            time.sleep(1)
            self.connect(user, password)

    def loop(self, timeout=None):
        if timeout:
            self.client.loop(timeout=timeout)
        else:
            self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()

    def _on_connect(self, client, userdata, flags, rc):
        log.info('on_connect %s' % rc)
        client.subscribe('video/cloudipcmgr/register')
        client.subscribe('video/cloudipcmgr/report')

    def _on_message(self, client, userdata, msg):
        log.info('cloud on_message')
        payload = json.loads(msg.payload.decode())

        self.term_sn = payload.get('term_sn')
        self.publish('video/edgeipcmr/' + self.term_sn,
                     self.get_response(msg.topic, payload))
        socketio, skip_sid = userdata
        socketio.emit('cloud_log', {'data': self.term_sn},
                      namespace='/edge', broadcast=True, skip_id=skip_sid)

    def publish(self, topic, data):
        (rc, final_mid) = self.client.publish(topic, json.dumps(data), qos=1)
        return rc, final_mid

    def disconnects(self):
        self.client.disconnect()

    def get_response(self, topic, payload):
        if topic == 'video/cloudipcmgr/register':
            return self.response_regiser(payload)
        else:
            return {}

    def response_regiser(self, payload):
        term_sn = payload.get('term_sn')
        data = {
            "time": get_utctime(),
            "cmd": "config"
        }
        if term_sn not in ['MG51T-09-S05-1200', 'MG51T-09-S05-1211']:
            data['type'] = 'ban'
        else:
            now_sign = generate_md5(ordered_dict(config))
            if now_sign != payload.get('sign'):
                data['type'] = 'overwrite'
                data.update({
                    "ml": [{
                        "features": [1, 2, 5],
                        "ip": "192.168.1.3",
                        "ipcs": ["192.168.1.110", "192.168.1.111"]
                    }],
                    "pusher": [{
                        "ip": "192.168.1.2",
                        "ipcs": ["192.168.1.110", "192.168.1.111"],
                        "status": [1, 0]
                    }]
                })
            else:
                data['type'] = 'ok'
        return data

    def tr_stram_cmd(self, term_sn):
        data = {
            "time": get_utctime(),
            "data": [
                {"max_duration": 0, "pusher": "192.168.1.2", "ipc":
                 "192.168.1.110"}
            ],
            "type": "stop",
            "cmd": "rt_stream"
        }
        self.publish('video/edgeipcmr/' + term_sn, data)

        emit('cloud_log', {'data': 'data:' +
                           json.dumps(data)}, namespace='/edge')
