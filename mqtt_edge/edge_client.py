import time
import json
import threading

from mqtt_base import MQTTClient
from utils.data_utils import generate_md5, ordered_dict, get_utctime
from utils.sql_utils import SqlUtil
from logger import log
from flask_socketio import emit


class EdgeClient(MQTTClient):
    """ 边缘网关设备mqtt客户端
    """

    def __init__(self, host, port,
                 term_sn=None, config=None, sqlite_path=None):
        super(EdgeClient, self).__init__(
            host, port, term_sn, config, sqlite_path)

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
        emit('edge_log', {'data': json.dumps(data)}, namespace='/edge')
        return rc, final_mid

    def run(self):
        """ 边缘设备启动loop和向云端发布注册信息
        """

        threads = []
        thread1 = threading.Thread(target=self.loop)
        thread2 = threading.Thread(target=self.publish,
                                   args=('video/cloudipcmgr/register',))
        thread1.setDaemon(True)
        threads.append(thread1)
        threads.append(thread2)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def set_config(self, config):
        """ 更新配置
        """
        sql_util = SqlUtil(self.sqlite_path)
        sql_util.connect()
        sql_util.update_config(config)
        sql_util.close()

        self.config = sql_util.config

    def _on_connect(self, client, userdata, flags, rc):
        log.info('e_edge on_connect %s' % rc)
        client.subscribe('video/edgeipcmr/' + self.term_sn)

    def _on_message(self, client, userdata, msg):
        log.info('e_edge on_message')

        payload = json.loads(msg.payload.decode())
        cmd = payload.get('cmd')
        cmd_type = payload.get('type')
        msg_time = payload.get('time')

        socketio, skip_sid = userdata
        socketio.emit(
            'edge_log', {'data': cmd_type},
            namespace='/edge', broadcast=True, skip_sid=skip_sid)

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
                log.info('非登记设备, 1秒后重新注册')
                time.sleep(1)
                self.publish('video/cloudipcmgr/register')
        elif cmd == 'rt_stream':
            if cmd_type == 'start':
                log.info('%s cloud命令start 开始推流' % msg_time)
            elif cmd_type == 'stop':
                log.info('%s cloud命令stop 停止推流' % msg_time)
