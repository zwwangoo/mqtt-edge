from utils.data_utils import get_utctime

from . import EdgeReport


class EdgeAIEvent(EdgeReport):

    def report_msg(self):
        return {
            "time": get_utctime(),
            "term_sn": self.term_sn,
            "data": {
                "type": "motion",
                "event": "start",
                "timestamp": 1564140943,
            },
            "type": "ai_event",
            "cmd": "report"
        }
