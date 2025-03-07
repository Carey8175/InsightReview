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
            password=self.config.database['password'],
            database=database
        )

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


if __name__ == '__main__':
    ck = CKClient()
    ck.has_data_for_date('BTC-USDT-SWAP', datetime(2024, 3, 21))
    ck.close()