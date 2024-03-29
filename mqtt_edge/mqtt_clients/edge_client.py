import json
import time

from . import MQTTClient
from utils.data_utils import generate_md5, ordered_dict, get_utctime
from utils.sql_utils import SqlUtil
from logger import log
from zmq_nodes.ipcmgr_node import IpcMgrNode
from zmq_nodes.peer_node import PeerNode


class EdgeClient(MQTTClient):
    """ 边缘网关设备mqtt客户端
    """

    def __init__(self, host, port,
                 term_sn=None, config=None, sqlite_path=None):

        self.sqlite_path = sqlite_path
        if not term_sn:
            self.term_sn, self.config = self.read_config()
        else:
            self.term_sn = term_sn
            self.config = config

        super(EdgeClient, self).__init__(host, port, client_id=term_sn)
        self.peers = {}
        self.evmgr = None

    def publish_register(self,
                         topic='video/cloudipcmgr/register',
                         data=None, qos=1):
        ordered = ordered_dict(self.config)
        md5_ordered = generate_md5(ordered)
        data = data or {
            'term_sn': self.term_sn,
            'sign': md5_ordered,
            'time': get_utctime()
        }
        return self.publish(topic, data, qos)

    def publish_report(self,
                       topic='video/cloudipcmgr/report',
                       data=None, qos=1):
        return self.publish(topic, data, qos)

    def read_config(self):
        """
        读取配置
        """
        sql_util = SqlUtil(self.sqlite_path)
        sql_util.connect()
        sql_util.read_config()
        sql_util.close()

        return sql_util.term_sn, json.loads(sql_util.config)

    def set_config(self, config):
        """ 更新配置
        """
        self.config = config
        sql_util = SqlUtil(self.sqlite_path)
        sql_util.connect()
        sql_util.update_config(config, self.term_sn)
        sql_util.close()

    def _on_connect(self, client, userdata, flags, rc):
        log.info('edge设备连接Broker')
        client.subscribe('video/edgeipcmr/' + self.term_sn)

    def _on_message(self, client, userdata, msg):
        log.info('edge接受到信息')

        payload = json.loads(msg.payload.decode())
        if 'cmd' in payload:
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
                    time.sleep(2)
                    self.publish_register()
            elif cmd == 'rt_stream':
                if cmd_type == 'start':
                    log.info('%s cloud命令start 开始推流' % msg_time)
                elif cmd_type == 'stop':
                    log.info('%s cloud命令stop 停止推流' % msg_time)
        elif 'data' in payload:
            data = payload.get('data')
            if 'services' in data:
                services = data.get('services')
                self.peers_daemon(services)

    def peers_daemon(self, services):
        evmgr_config = services.pop('evmgr')
        self.create_evmgr(evmgr_config)

        # 根据配置创建同辈节点
        for peer_config in services.values():
            if isinstance(peer_config, list):
                for config in peer_config:
                    self.create_peer(config)
            elif isinstance(peer_config, dict):
                self.create_peer(peer_config)
            else:
                assert ValueError, 'data error'

        # self.create_peer(services.get('evpusher')[0])
        # self.create_peer(services.get('evpuller')[0])
        # self.create_peer(services.get('evslicer')[0])
        # self.create_peer(services.get('evml')[0])

    def create_evmgr(self, config):
        ident = config.get('sn') + str(config['iid'])
        if not self.evmgr:
            self.evmgr = IpcMgrNode(ident)
            self.evmgr.recv_loop()
        return self.evmgr

    def create_peer(self, config):
        ident = config.get('sn') + str(config['iid'])
        if ident in self.peers:
            return

        peer_node = PeerNode(ident, self.evmgr.ident)
        peer_node.recv_loop()
        peer_node.ready()

        self.peers[ident] = peer_node
