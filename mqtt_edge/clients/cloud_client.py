'''
模拟云端的client
'''
from logger import log
import json

from . import MQTTClient
from utils.data_utils import generate_md5, ordered_dict, get_utctime

from sqlalchemy import create_engine, text

db = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/cloud_db')


class CloudClient(MQTTClient):
    def __init__(self, host, port, keepalive=60):

        super(CloudClient, self).__init__(host, port,
                                          client_id='cloud',
                                          keepalive=keepalive)

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

    def get_response(self, topic, payload):
        if topic == 'video/cloudipcmgr/register':
            return self.response_regiser(payload)
        else:
            log.info('事件上报')
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
            print(term_config)
            now_sign = generate_md5(ordered_dict(term_config))
            if now_sign != payload.get('sign'):
                data['type'] = 'overwrite'
                data.update(term_config)
            else:
                data['type'] = 'ok'
        return data

    def publish_cmd(self, term_sn):
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
