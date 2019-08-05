import json
import sqlite3
from logger import log


class SqlUtil:

    def __init__(self, path):
        self.path = path
        self._term_sn = ''
        self._config = ''

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.path)
            self.cursor = self.conn.cursor()
        except Exception as e:
            log.error('Database ConnectionError')
            log.error(e)
            self.close()

    def read_config(self):
        # TODO 根据SQLite的数据结构更改sql语句
        self.cursor.execute(r'select term_sn, config from edge')
        info = self.cursor.fetchone()
        if info:
            self._term_sn = info[0]
            self._config = info[1]

    def update_config(self, config):
        self._config = config
        self.cursor.execute("update edge set config='{}'"
                            .format(json.dumps(config)))
        self.conn.commit()

    @property
    def term_sn(self):
        return self._term_sn

    @property
    def config(self):
        return self._config

    def close(self):
        self.cursor.close()
        self.conn.close()
