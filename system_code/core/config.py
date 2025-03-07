import os
import json
from loguru import logger


class Config:
    ROOT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATICS_PATH = os.path.join(ROOT_PATH, 'statics')
    CONFIG_PATH = os.path.join(STATICS_PATH, 'config.json')
    MODEL_DIR = os.path.join(STATICS_PATH, 'models')  # 定义模型文件夹路径

    def __init__(self):
        self.proxy = None
        self.webhook = None
        self.database = None
        # ---------------
        self.init_config()

    def init_config(self) -> None:
        if not os.path.exists(self.CONFIG_PATH):
            logger.error('config.json not found at {}'.format(self.CONFIG_PATH))

            return

        with open(self.CONFIG_PATH, 'r') as f:
            config = json.load(f)

        self.database = config['database']


if __name__ == '__main__':
    config = Config()
    print(config.key.get_params())
