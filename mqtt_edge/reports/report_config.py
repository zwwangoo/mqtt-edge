from utils.data_utils import get_utctime

from config import config as Config
from . import EdgeReport


class EdgeConfig(EdgeReport):

    def report_msg(self):
        return {
            "time": get_utctime(),
            "term_sn": self.term_sn,
            "data": [
                {
                    "module": "ml",
                    "ip": "192.168.1.3",
                    "reason": "failed to connect ipc 192.168.1.111"
                }
            ],
            "type": "config",
            "cmd": "report"
        }


def run():
    config = EdgeConfig(Config.HOST, Config.PORT, Config.SQLITE_PATH)
    config.connect()
    config.publish()
