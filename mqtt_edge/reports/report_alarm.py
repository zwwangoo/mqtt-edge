from utils.data_utils import get_utctime

from config import config as Config
from . import EdgeReport


class EdgeAlarm(EdgeReport):

    def report_msg(self):
        return {
            "time": get_utctime(),
            "term_sn": self.term_sn,
            "data": [
                {
                    "name": "self",
                    "alarms": [{"tag": "cpu", "value": 99.2}]
                },
                {
                    "name": "pusher",
                    "ip": "192.168.1.2",
                    "alarms": [{"tag": "ram", "value": 4.2}]
                },
                {
                    "name": "pusher",
                    "ip": "192.168.1.5",
                    "alarms": [{"tag": "disk", "value": 3.3}]
                }
            ],
            "type": "alarm",
            "cmd": "report"
        }


def run():
    alarm = EdgeAlarm(Config.HOST, Config.PORT, Config.SQLITE_PATH)
    alarm.connect()
    alarm.publish()
