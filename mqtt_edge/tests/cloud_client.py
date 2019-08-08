'''
模拟云端的client
'''
from logger import log
import json

from paho.mqtt.client import Client
from utils.data_utils import generate_md5, ordered_dict, get_utctime

from sqlalchemy import create_engine, text

db = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/cloud_db')


class CloudClient:
    def __init__(self, host, port, keepalive=60):

        self.client = Client(client_id='cloud', clean_session=False)

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.connected = False

    def connect(self, user='admin', password='password'):
        self.client.username_pw_set(user, password)
        try:
            self.client.connect(self.host, self.port, self.keepalive)
            self.connected = True

        except ConnectionRefusedError as e:
            log.error(e)
            log.info('Retry after 1 second.')

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

        print(payload)
        self.term_sn = payload.get('term_sn')
        self.publish('video/edgeipcmr/' + self.term_sn,
                     self.get_response(msg.topic, payload))

    def publish(self, topic, data):
        (rc, final_mid) = self.client.publish(topic, json.dumps(data), qos=1)
        return rc, final_mid

    def disconnect(self):
        self.connected = False
        self.client.disconnect()

    def get_response(self, topic, payload):
        if topic == 'video/cloudipcmgr/register':
            return self.response_regiser(payload)
        else:
            log.info('report successed')
            return {}

    def response_regiser(self, payload):
        term_sn = payload.get('term_sn')
        data = {
            "time": get_utctime(),
            "cmd": "config"
        }
        term = db.execute(
            text('select term_sn, config from edge where term_sn=:term_sn'),
            {'term_sn': term_sn}).fetchone()
        if not term:
            data['type'] = 'ban'
        else:
            term_config = json.loads(term.config)
            now_sign = generate_md5(ordered_dict(term_config))
            if now_sign != payload.get('sign'):
                data['type'] = 'overwrite'
                data.update(term_config)
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
