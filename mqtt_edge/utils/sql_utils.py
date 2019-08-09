import json
import sqlite3
from decimal import Decimal
from logger import log
from extensions import db


class SqlUtil:

    def __init__(self, path, term_sn=None):
        self.path = path

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.path)
            self.cursor = self.conn.cursor()
        except Exception as e:
            log.error('Database ConnectionError')
            log.error(e)
            self.close()

    def read_config(self, term_sn=None):
        # TODO 根据SQLite的数据结构更改sql语句
        if term_sn:
            exec = self.cursor.execute(
                'select term_sn, config from edge where term_sn="{}"'
                .format(term_sn))
        else:
            exec = self.cursor.execute('select term_sn, config from edge')

        return exec.fetchone()

    def update_config(self, config, term_sn):
        if self.read_config(term_sn):
            self.cursor.execute(
                "update edge set config='{}' where term_sn='{}'"
                .format(json.dumps(config), term_sn))
        else:
            self.cursor.execute(
                r"insert into edge values ('{term_sn}', '{config}')"
                .format(term_sn=term_sn, config=json.dumps(config)))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()


class RowProxyDict(dict):
    """
    自定义字典类型，处理执行查询SQL返回的结果。
    1 将大写键值转换成小写。
    2 当键不存在时，不抛出异常，而是返回None。

    需要注意的是:

    >>> my_dict = RowProxyDict()
    >>> my_dict.id = 10
    >>> print(my_dict.ID)
    10
    >>> 'ID' in mydict
    False
    >>> 'id' in mydict
    True
    >>> mydict['name'] = 'wen'
    >>> mydict['Name']
    'wen'
    """

    def __init__(self, **kw):
        super(RowProxyDict, self).__init__(**kw)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def __setitem__(self, key, value):
        super(RowProxyDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        key = key.lower()
        return self.get(key, None)


def row_format(row):
    """
    对 SQL 结果进行dict类型转换
    """
    row_dict = RowProxyDict()
    if not row:
        return row_dict
    for (key, value) in row.items():
        if isinstance(value, Decimal):
            # 对数据库中出现的长 decimal 类型，
            # python 的 float 会转换成科学计数法形式的处理
            value = str(value) if 'e' in str(float(value)) else float(value)
        row_dict[key] = value
    return row_dict


def fetchall(sql, params={}):
    """
    获取多个SQL执行结果
    """
    results = db.session.execute(sql, params).fetchall()
    beans = []
    for row in results:
        beans.append(row_format(row))
    return beans


def fetchone(sql, params={}):
    """
    获取一个SQL执行结果
    """
    result = db.session.execute(sql, params).fetchone()
    return row_format(result)
