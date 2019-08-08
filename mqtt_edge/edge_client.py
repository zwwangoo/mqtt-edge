import json

from mqtt_base import MQTTClient
from utils.data_utils import generate_md5, ordered_dict, get_utctime
from utils.sql_utils import SqlUtil
from logger import log


class EdgeClient(MQTTClient):
    """ 边缘网关设备mqtt客户端
    """

    def __init__(self, host, port,
                 term_sn=None, config=None, sqlite_path=None):
        super(EdgeClient, self).__init__(
            host, port, term_sn=term_sn,
            config=config, sqlite_path=sqlite_path)

    def publish(self, topic, data=None, qos=1):
        """ 发布消息
        """

        ordered = ordered_dict(self.config)
        md5_ordered = generate_md5(ordered)
        data = {
            'term_sn': self.term_sn,
            'sign': md5_ordered,
            'time': get_utctime()
        }

        (rc, final_mid) = self.client.publish(topic, json.dumps(data), qos=qos)
        return rc, final_mid

    def set_config(self, config):
        """ 更新配置
        """
        self.config = config
        sql_util = SqlUtil(self.sqlite_path)
        sql_util.connect()
        sql_util.update_config(config, self.term_sn)
        sql_util.close()

    def _on_connect(self, client, userdata, flags, rc):
        log.info('e_edge on_connect %s' % rc)
        client.subscribe('video/edgeipcmr/' + self.term_sn)

    def _on_message(self, client, userdata, msg):
        log.info('e_edge on_message')

        payload = json.loads(msg.payload.decode())
        cmd = payload.get('cmd')
        cmd_type = payload.get('type')
        msg_time = payload.get('time')

        if cmd == 'config':
            if cmd_type == 'overwrite':
                self.config = {
                    'ml': payload.get('ml'),
                    'pusher': payload.get('pusher')
                }
                self.set_config(self.config)
                log.info('更新配置config')
            elif cmd_type == 'ok':
                log.info('注册成功')
            elif cmd_type == 'ban':
                log.info('非登记设备')
        elif cmd == 'rt_stream':
            if cmd_type == 'start':
                log.info('%s cloud命令start 开始推流' % msg_time)
            elif cmd_type == 'stop':
                log.info('%s cloud命令stop 停止推流' % msg_time)
