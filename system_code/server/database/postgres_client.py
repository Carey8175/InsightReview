import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import pandas as pd
from system_code.core.config import Config, logger

class PGClient:
    def __init__(self):
        self.config = Config()
        self.conn = psycopg2.connect(
            host=self.config.postgresql['host'],
            port=self.config.postgresql['port'],
            user=self.config.postgresql['user'],
            password=self.config.postgresql['password'],
            database=self.config.postgresql['database']
        )
        self.database_validation()

    def execute(self, query, params=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)
            if cursor.description:
                return cursor.fetchall()
            self.conn.commit()

    def insert_dataframe(self, table, df):
        with self.conn.cursor() as cursor:
            columns = ', '.join(df.columns)
            values = ', '.join(['%s'] * len(df.columns))
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
                sql.Identifier(table),
                sql.SQL(', ').join(map(sql.Identifier, df.columns)),
                sql.SQL(', ').join([sql.Placeholder()]*len(df.columns))
            )
            for _, row in df.iterrows():
                cursor.execute(query, tuple(row))
            self.conn.commit()

    def close(self):
        self.conn.close()

    def database_validation(self):
        try:
            # Create database if not exists
            conn = psycopg2.connect(
                host=self.config.postgresql['host'],
                user=self.config.postgresql['user'],
                password=self.config.postgresql['password'],
                port=self.config.postgresql['port']
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("CREATE DATABASE IF NOT EXISTS {}").format(
                    sql.Identifier(self.config.postgresql['database']))
                )

            # Create table if not exists
            self.execute('''
                CREATE TABLE IF NOT EXISTS product_reviews (
                    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    rating FLOAT,
                    title TEXT,
                    text TEXT,
                    images TEXT[],
                    asin TEXT,
                    parent_asin TEXT,
                    user_id TEXT,
                    timestamp BIGINT,
                    verified_purchase BOOLEAN,
                    helpful_vote INTEGER,
                    real_review BOOLEAN DEFAULT FALSE,
                    sentiment TEXT DEFAULT '',
                    summary TEXT DEFAULT ''
                )
            ''')
            logger.info('[PGClient] Database validation completed')
        except Exception as e:
            logger.error(f'Database validation failed: {str(e)}')