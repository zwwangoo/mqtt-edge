import json
from edge_client import EdgeClient


class EdgeReport(EdgeClient):

    def __init__(self, host, port,
                 sqlite_path=None, term_sn=None, config=None):
        super(EdgeReport, self).__init__(host, port,
                                         sqlite_path=sqlite_path,
                                         term_sn=term_sn, config=config)

    def publish(self):
        data = self.report_msg()
        topic = 'video/cloudipcmgr/report'

        self.client.publish(topic, json.dumps(data), qos=1)

    def report_msg(self):
        return {}
