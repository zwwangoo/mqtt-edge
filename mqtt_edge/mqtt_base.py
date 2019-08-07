import time
import json
from paho.mqtt.client import Client
from flask_socketio import emit

from logger import log
from utils.sql_utils import SqlUtil


class MQTTClient:
    """ mqtt客户端的父类
    """

    def __init__(self, host, port, sqlite_path,
                 term_sn=None,
                 config=None,
                 keepalive=60):

        self.client = Client()
        self.sqlite_path = sqlite_path
        if not term_sn:
            self.term_sn, self.config = self._read_config()
        else:
            self.term_sn = term_sn
            self.config = config

        # client_id 值取term_sn，这样就保证了只有一个client，再断线重连
        # 之后就可以收到断线期间的订阅信息
        self.client._client_id = self.term_sn
        self.client._clean_session = False

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self.connected = False

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_log = self._on_log

    def connect(self, user='admin', password='password'):
        rc = 1
        if self.connected:
            return 0

        self.client.username_pw_set(user, password)
        try:
            rc = self.client.connect(self.host, self.port, self.keepalive)
            assert rc == 0, ConnectionRefusedError
            self.connected = True

            emit('edge_log', {
                 'data': '{} edge connected.'.format(self.term_sn)})

        except ConnectionRefusedError:
            log.error('Retry after 1 second.')

            emit('edge_log', {
                 'data': 'ConnectionResetError, Retry after 1 second.'})

            time.sleep(1)
            self.connect(user, password)
        return rc

    def loop(self, timeout=None):
        if timeout:
            self.client.loop(timeout=timeout)
        else:
            self.client.loop_forever()

    def loop_start(self):
        return self.client.loop_start()

    def _read_config(self):
        """
        读取配置
        """
        sql_util = SqlUtil(self.sqlite_path)
        sql_util.connect()
        sql_util.read_config()
        sql_util.close()

        return sql_util.term_sn, json.loads(sql_util.config)

    def publish(self):
        pass

    def _on_connect(self, client, userdata, flags, rc):
        pass

    def _on_message(self, client, userdata, msg):
        pass

    def _on_log(self, client, userdata, level, buf):
        return buf
