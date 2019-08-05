"""
模拟云端
"""
import time
from config import config as Config
from tests.cloud_client import CloudClient

if __name__ == '__main__':
    client = CloudClient(Config.HOST, Config.PORT)
    client.connect()
    client.loop_start()

    while True:
        time.sleep(5)
        client.tr_stram_cmd()
