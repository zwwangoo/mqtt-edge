import zmq
import time
import json
from threading import Thread

from utils.data_utils import encode


class IpcMgrNode:
    context = zmq.Context()

    mgr = context.socket(zmq.ROUTER)
    poller = zmq.Poller()

    def __init__(self, ident):

        self._ident = ident
        self.mgr.setsockopt(zmq.IDENTITY, encode(ident))
        self.mgr.bind('tcp://*:5555')
        self.poller.register(self.mgr, zmq.POLLIN)

    @property
    def ident(self):
        return self._ident

    def send(self, data, addr):

        data = [encode(addr), encode(data)]
        print(self.ident + ': 给 %s 发送消息' % (addr,))
        self.mgr.send_multipart(data)

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
                continue
            if socks.get(self.mgr) == zmq.POLLIN:
                msg = self.mgr.recv_multipart()
                if len(msg) == 3:
                    print(self.ident + ': 做了一次转发信息给%s' % msg[1])
                    self.send(msg[2], msg[1])
                elif msg[-1] == b'READY':
                    print(self.ident + ': %s 设备准备完毕' % msg[0])
                    self.send(b'Update Config', msg[0])
                else:
                    print(self.ident + ': 收到来自%s 的信息 %s' % (msg[0], msg[-1]))

    def _to_json(self, data):
        try:
            r_dict = json.loads(data)
        except json.decoder.JSONDecodeError:
            return data, False
        else:
            return r_dict, True


if __name__ == '__main__':
    mgr = IpcMgrNode('ILS-11')
    mgr.recv_loop()

    while True:
        time.sleep(2)
        mgr.send('Hi, I am edge_ipc', 'ILS-13')
