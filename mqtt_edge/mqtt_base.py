import time
import json
from paho.mqtt.client import Client

from logger import log
from utils.sql_utils import SqlUtil


class MQTTClient:
    """ mqtt客户端的父类
    """

    def __init__(self, host, port, sqlite_path, keepalive=60):
        self.sqlite_path = sqlite_path
        self.term_sn, self.config = self._read_config()

        # client_id 值取term_sn，这样就保证了只有一个client，再断线重连
        # 之后就可以收到断线期间的订阅信息
        self.client = Client(client_id=self.term_sn, clean_session=False)

        self.host = host
        self.port = port
        self.keepalive = keepalive

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def connect(self, user='admin', password='password'):
        self.client.username_pw_set(user, password)
        try:
            self.client.connect(self.host, self.port, self.keepalive)
        except ConnectionRefusedError as e:
            log.error(e)
            log.info('Retry after 1 second.')
            time.sleep(1)
            self.connect(user, password)

    def loop(self, timeout=None):
        if timeout:
            self.client.loop(timeout=timeout)
        else:
            self.client.loop_forever()

    def loop_start(self):
        self.client.loop_start()

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
