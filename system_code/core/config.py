import os
import json
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path


class Config:
    ROOT_PATH = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATICS_PATH = Path(os.path.join(ROOT_PATH, 'statics'))
    CONFIG_PATH = STATICS_PATH / 'config.json'
    MODEL_DIR = STATICS_PATH / 'models'
    # Load environment variables from .env file
    load_dotenv(STATICS_PATH / '.env')

    def __init__(self):
        self.proxy = None
        self.webhook = None
        self.postgresql = None
        self.volcengine = None
        # ---------------
        self.init_config()

    def init_config(self) -> None:
        if not os.path.exists(self.CONFIG_PATH):
            logger.error('config.json not found at {}'.format(self.CONFIG_PATH))

            return

        with open(self.CONFIG_PATH, 'r') as f:
            config = json.load(f)

        self.postgresql = config['database']
        self.volcengine = {
            'ak': os.getenv('VOLCENGINE_AK'),
            'sk': os.getenv('VOLCENGINE_SK'),
            'collection_name': os.getenv('COLLECTION_NAME')
        }


if __name__ == '__main__':
    config = Config()
    print(config.volcengine)
