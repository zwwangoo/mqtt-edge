import zmq
import time
import json
from threading import Thread
from utils.data_utils import encode


class PeerNode:

    context = zmq.Context()

    def __init__(self, ident, edge_ipc):
        self.node = self.context.socket(zmq.ROUTER)
        self.poller = zmq.Poller()
        self.ident = ident
        self.node.setsockopt(zmq.IDENTITY, encode(ident))
        self.node.connect('tcp://localhost:5555')
        self.edge_ipc = encode(edge_ipc)
        self.poller.register(self.node, zmq.POLLIN)

    def ready(self):
        # TODO 有一个问题，ROUTER 套接字会直接丢弃无法路由的信息!
        # 建立连接之后，立即发送一条消息，该条消息会丢失的。
        # 这里硬生生的停了1秒！
        time.sleep(1)
        self.send('READY')

    def send(self, data, addr=None):

        data = encode(data)
        if addr:
            addr = encode(addr)
            data = [self.edge_ipc, addr, data]
            print(self.ident + ': 消息将会被%s转发给%s' % (self.edge_ipc, addr))
        else:
            data = [self.edge_ipc, data]
            print(self.ident + ': 消息发送给 %s' % (self.edge_ipc,))
        self.node.send_multipart(data)

    def loop(self):
        while True:
            # 我只是一个不停止的循环
            pass

    def recv_loop(self):
        # 单开线程，不会阻塞
        t = Thread(target=self._recv_loop)
        t.daemon = True
        t.start()

    def _recv_loop(self):

        while True:
            try:
                socks = dict(self.poller.poll())
            except zmq.ZMQError:
                break
            if socks.get(self.node) == zmq.POLLIN:
                msg = self.node.recv_multipart()
                if len(msg) == 2:
                    [addr, msg] = msg
                    data, rc = self._to_json(msg.decode())
                    if rc and 'cmd' in data:
                        print(self.ident + ': 收到命令：', data.get('cmd'))
                    else:
                        print(self.ident + ': 收到来自 %s 的信息：%s' % (addr, msg))
                else:
                    print(self.ident + ': 非法信息', msg)

    def _to_json(self, data):
        try:
            r_dict = json.loads(data)
        except json.decoder.JSONDecodeError:
            return data, False
        else:
            return r_dict, True


if __name__ == '__main__':
    node = PeerNode('ILS-23', 'ILS-11')
    node.recv_loop()
    node.ready()
    while True:
        time.sleep(5)
        node.send('I am ILS_23', 'ILS-22')
