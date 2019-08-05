import time
import hashlib


def generate_md5(data):
    """
    MD5加密处理
    """
    hl = hashlib.md5()
    hl.update(data.encode(encoding='utf-8'))
    return hl.hexdigest()


def get_utctime():
    """
    获取UTC时间戳
    """
    return int(time.strftime('%s', time.gmtime(time.time())))


def ordered_dict(data):
    """
    将dict转换成有序的str
    """
    return get_str(data)


def get_str(data):
    """
    判断数据类型进行转换
    """
    if isinstance(data, dict):
        value = dict_to_ordered_str(data)
    elif isinstance(data, list):
        value = list_to_str(data)
    else:
        value = '"{}"'.format(data) if isinstance(
            data, str) else '{}'.format(data)

    return value


def dict_to_ordered_str(data):
    """
    将dict转换成有序的str
    dict可能会存在多层嵌套的情况
    """
    ordered = ''
    tuple_data = sorted(data.items(), key=lambda x: x[0])
    for item in tuple_data:
        value = get_str(item[1])
        ordered += '"{}": {}, '.format(item[0], value)
    ordered = ordered[:-2]
    return '{' + ordered + '}'


def list_to_str(data):
    """
    将list转换成str，其中list中可能含有dict
    """
    ordered = ''
    for item in data:
        value = get_str(item)
        ordered += value + ', '
    ordered = ordered[:-2]
    return '[' + ordered + ']'


if __name__ == '__main__':

    pr = ordered_dict({
        'c': [{
            'c': 'nihao',
            'b': {
                'cc': [{
                    'dc': '命令',
                    'cd': 'adf'
                }],
                'ca': ['12', '13']
            }
        }],
        'a': '顺序'
    })
    print(pr)
    print(generate_md5(pr))
    print(get_utctime())
