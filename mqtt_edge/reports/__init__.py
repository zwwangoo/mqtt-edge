import json
from edge_client import EdgeClient


class EdgeReport(EdgeClient):

    def __init__(self, host, port, sqlite_path):
        super(EdgeReport, self).__init__(host, port, sqlite_path)

    def publish(self):
        data = self.report_msg()
        topic = 'video/cloudipcmgr/report'

        self.client.publish(topic, json.dumps(data), qos=1)

    def report_msg(self):
        return {}
