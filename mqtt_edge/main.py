from config import config as Config
from edge_client import EdgeClient

if __name__ == '__main__':
    client = EdgeClient(Config.HOST, Config.PORT, Config.SQLITE_PATH)
    client.connect(Config.USER, Config.PASSWORD)
    client.run()
