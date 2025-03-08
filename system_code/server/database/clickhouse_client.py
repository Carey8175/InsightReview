import os.path

import clickhouse_driver
from datetime import datetime

import pandas as pd

from system_code.core.config import Config, logger


class CKClient:
    def __init__(self, database='mc'):
        self.config = Config()
        self.client = clickhouse_driver.Client(
            host=self.config.database['host'],
            port=self.config.database['port'],
            user=self.config.database['user'],
            password=self.config.database['password']
        )

        self.database_validation()

    def execute(self, query):
        return self.client.execute(query)

    def insert(self, table, data, columns=None):
        if columns is None:
            columns = []

        col_str = "(" + ", ".join(columns) + ")" if columns else ""
        sql = f"INSERT INTO {table} {col_str} VALUES"

        self.client.execute(sql, data)

    def close(self):
        self.client.disconnect()

    def merge_table(self, table):
        sql = f"OPTIMIZE TABLE {table} FINAL;"
        self.execute(sql)

    def query_dataframe(self, query):
        return self.client.query_dataframe(query)

    def get_columns(self, table) -> list:
        """
        获取指定表的所有列名
        :param table: 表名
        :return: 列名列表
        """
        sql = f"""
        SELECT name 
        FROM system.columns 
        WHERE table = '{table}' AND database = '{self.client.connection.database}'
        """

        result = self.execute(sql)

        return [row[0] for row in result] if result else []

    def database_validation(self):
        """检测数据库是否正确，表格是否创建，没有创建的话就自动创建"""
        self.create_database()
        self.create_table()

        # 如果当前表格为空是否插入数据
        sql = f"SELECT COUNT(*) FROM {self.config.database['table']}"
        result = self.execute(sql)
        if result[0][0] == 0:
            logger.info('Table product_reviews is empty, inserting data...')
            for i in range(3):
                data = pd.read_csv(os.path.join(self.config.STATICS_PATH, 'datasets', 'reviews', 'csv', f'All_Beauty_part_{i+1}.csv'))
                data = data.astype({
                    'rating': 'float32',              # 对应 ClickHouse 的 Float32
                    'title': 'string',                 # 对应 ClickHouse 的 String
                    'text': 'string',                  # 对应 ClickHouse 的 String
                    'images': 'object',                # ClickHouse 里是 Array(String)，Pandas 里用 object 处理列表
                    'asin': 'string',                   # 对应 ClickHouse 的 String
                    'parent_asin': 'string',            # 对应 ClickHouse 的 String
                    'user_id': 'string',                 # 对应 ClickHouse 的 String
                    'timestamp': 'int64',                # 对应 ClickHouse 的 UInt64
                    'verified_purchase': 'bool',         # 对应 ClickHouse 的 Bool
                    'helpful_vote': 'int32'              # 对应 ClickHouse 的 UInt32
                })
                data = data.fillna("")
                columns = data.columns.tolist()
                data = data.values.tolist()
                self.insert(self.config.database['table'], data, columns=columns)
            logger.info('Data inserted.')

        logger.info('[CKClient]Database validation completed.')

    def create_database(self):
        sql = f"CREATE DATABASE IF NOT EXISTS {self.config.database['database']}"
        self.execute(sql)

        # 链接到数据库
        self.client.execute(f"USE {self.config.database['database']}")
        # logger.info(f"Database {self.client.connection.database} created.")

    def create_table(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database['table']}(
            review_id UUID DEFAULT generateUUIDv4(),
            rating Float32,
            title String,
            text String,
            images Array(String),
            asin String,
            parent_asin String,
            user_id String,
            timestamp UInt64,
            verified_purchase Bool,
            helpful_vote UInt32
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, review_id);
        """

        self.execute(sql)
        # logger.info('Table product_reviews created.')



if __name__ == '__main__':
    ck = CKClient()
