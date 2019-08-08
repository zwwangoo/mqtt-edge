import json
from paho.mqtt.client import Client

from logger import log


class MQTTClient:
    """ mqtt客户端的父类
    """

    def __init__(self, host, port,
                 client_id=None,
                 clean_session=False,
                 keepalive=60):

        self.client = Client()
        if client_id:
            self.client._client_id = client_id
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

        except ConnectionRefusedError:
            log.error('Retry after 1 second.')

        return rc

    def disconnect(self):
        self.connected = False
        self.client.disconnect()

    def loop(self, timeout=None):
        if timeout:
            self.client.loop(timeout=timeout)
        else:
            self.client.loop_forever()

    def loop_start(self):
        return self.client.loop_start()

    def publish(self, topic, data={}, qos=1):
        (rc, final_mid) = self.client.publish(topic, json.dumps(data), qos=qos)
        return rc, final_mid

    def _on_connect(self, client, userdata, flags, rc):
        pass

    def _on_message(self, client, userdata, msg):
        pass

    def _on_log(self, client, userdata, level, buf):
        return buf
