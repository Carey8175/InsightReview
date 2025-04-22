from ast import main
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime
import pandas as pd
from tqdm import tqdm
from system_code.core.config import Config, logger
import json # Add json import for parsing images string

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
            # Check if the cursor has results to fetch
            if cursor.description:
                results = cursor.fetchall()
                self.conn.commit() # Commit after fetch if needed, though typically SELECT doesn't need commit
                return results
            else:
                # For INSERT, UPDATE, DELETE, etc., commit the transaction
                self.conn.commit()
                return None # Indicate no rows returned

    def insert_dataframe(self, table, df):
        # Note: This row-by-row insert can be slow for large dataframes.
        # Consider using psycopg2.extras.execute_values or COPY for bulk inserts.
        with self.conn.cursor() as cursor:
            columns = ', '.join(df.columns)
            values_template = ', '.join(['%s'] * len(df.columns))
            # Use sql.SQL for safe identifier quoting
            query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) ON CONFLICT (review_id) DO NOTHING").format(
                sql.Identifier(table),
                sql.SQL(', ').join(map(sql.Identifier, df.columns)),
                sql.SQL(', ').join([sql.Placeholder()] * len(df.columns))
            )
            # Convert DataFrame rows to tuples for insertion
            data_tuples = [tuple(x) for x in df.to_numpy()]
            # Use execute_batch for potentially better performance than iterating
            # Note: execute_batch might still be slower than execute_values or COPY
            # psycopg2.extras.execute_batch(cursor, query, data_tuples)
            # Fallback to row-by-row if execute_batch is not preferred or available in basic psycopg2
            for row_tuple in data_tuples:
                try:
                    cursor.execute(query, row_tuple)
                except Exception as e:
                    logger.error(f"Error inserting row: {row_tuple}. Error: {e}")
                    self.conn.rollback() # Rollback the specific failed row insert if desired, or handle differently
                    # Optionally, continue to the next row or re-raise the exception
                    continue
            self.conn.commit()

    def init_reviews(self, csv_files):
        """Loads review data from a list of CSV files into the beauty_reviews table."""
        logger.info(f"Starting review initialization from files: {csv_files}")
        required_columns = [
            'rating', 'title', 'text', 'images', 'asin', 'parent_asin',
            'user_id', 'timestamp', 'verified_purchase', 'helpful_vote'
        ]
        # Define expected data types for conversion
        dtype_map = {
            'rating': float,
            'title': str,
            'text': str,
            'images': str, # Keep as string initially for parsing
            'asin': str,
            'parent_asin': str,
            'user_id': str,
            'timestamp': 'Int64', # Use pandas Int64 for nullable integers
            'verified_purchase': bool,
            'helpful_vote': 'Int64' # Use pandas Int64 for nullable integers
        }

        for file_path in csv_files:
            try:
                logger.info(f"Processing file: {file_path}")
                # Read CSV with specified dtypes, handle potential parsing errors
                df = pd.read_csv(file_path, dtype=dtype_map, low_memory=False)

                # Basic validation: Check if required columns exist
                if not all(col in df.columns for col in required_columns):
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    logger.error(f"File {file_path} is missing required columns: {missing_cols}. Skipping file.")
                    continue

                # Select and reorder columns to match the target table structure (optional but good practice)
                df = df[required_columns].copy()

                # Data Cleaning and Transformation
                df.fillna({
                    'title': '',
                    'text': '',
                    'images': '[]', # Default empty JSON array string for images
                    'asin': '',
                    'parent_asin': '',
                    'user_id': '',
                    'timestamp': 0, # Default timestamp if missing
                    'helpful_vote': 0 # Default helpful_vote if missing
                }, inplace=True)

                # Convert boolean explicitly if needed (read_csv might handle it)
                df['verified_purchase'] = df['verified_purchase'].astype(bool)

                # Convert nullable integers to standard int, handling pd.NA
                df['timestamp'] = df['timestamp'].fillna(0).astype(int)
                df['helpful_vote'] = df['helpful_vote'].fillna(0).astype(int)

                # Handle 'images' column: Convert string representation to list of strings (TEXT[])
                def parse_images(image_str):
                    if pd.isna(image_str) or not image_str or image_str == '[]':
                        return []
                    try:
                        # Replace single quotes with double quotes for valid JSON
                        image_str = image_str.replace("'", '"')
                        images_list = json.loads(image_str)
                        # Extract 'large_image_url' or another relevant field if needed, otherwise keep the structure
                        # For TEXT[], we might just store the URLs
                        urls = [img.get('large_image_url', '') for img in images_list if isinstance(img, dict)]
                        return [url for url in urls if url] # Filter out empty strings
                    except json.JSONDecodeError:
                        # Handle cases where the string is not valid JSON or not a list
                        # If it's a single URL or malformed, return it in a list or handle as needed
                        if image_str.startswith('http'):
                             return [image_str]
                        logger.warning(f"Could not parse images string: {image_str[:100]}...")
                        return [] # Return empty list if parsing fails
                    except Exception as e:
                         logger.warning(f"Error processing images string: {image_str[:100]}... Error: {e}")
                         return []

                df['images'] = df['images'].apply(parse_images)

                # Add default columns if they don't exist
                df['real_review'] = False
                df['sentiment'] = ''
                df['summary'] = ''

                # Ensure columns match the table definition order if necessary before insert
                # Example: df = df[['review_id', 'rating', ...]] # Assuming review_id is generated by DB

                logger.info(f"Inserting {len(df)} rows from {file_path} into beauty_reviews table.")
                self.insert_dataframe('beauty_reviews', df)
                logger.info(f"Finished inserting data from {file_path}.")

            except FileNotFoundError:
                logger.error(f"File not found: {file_path}. Skipping.")
            except pd.errors.EmptyDataError:
                logger.warning(f"File is empty: {file_path}. Skipping.")
            except Exception as e:
                logger.error(f"Failed to process file {file_path}: {str(e)}")

        logger.info("Review initialization process completed.")

    def process_and_update_reviews(self):
        """Fetches reviews, processes text using TextAnalysis, and updates the table."""
        try:
            from system_code.core.text_analysis import TextAnalysis # Import here to avoid circular dependency if TextAnalysis uses PGClient
            text_analyzer = TextAnalysis()
            logger.info("Starting review text processing and update.")

            with self.conn.cursor() as cursor:
                # Fetch review_id and text for processing
                # Assuming 'review_id' is the primary key or a unique identifier
                # Adjust column names if they are different
                cursor.execute("SELECT review_id, text FROM beauty_reviews WHERE sentiment = '' OR summary = '' OR real_review IS NULL") # Process only unprocessed rows
                reviews_to_process = cursor.fetchall()
                total_reviews = len(reviews_to_process)

                processed_count = 0
                for review_id, text in tqdm(reviews_to_process, desc=f"Processing reviews, total {total_reviews}"):
                    try:
                        if not text: # Skip if text is empty or null
                            logger.warning(f"Skipping review_id {review_id} due to empty text.")
                            continue

                        # Process the text
                        sentiment, is_real, summary = text_analyzer.single_process(text)
                        # Map is_real (int 0 or 1) to real_review (boolean)
                        real_review = bool(is_real)

                        # Update the database record
                        update_query = sql.SQL("""
                            UPDATE beauty_reviews
                            SET sentiment = %s, real_review = %s, summary = %s
                            WHERE review_id = %s
                        """)
                        cursor.execute(update_query, (sentiment, real_review, summary, review_id))
                        processed_count += 1
                        if processed_count % 100 == 0: # Log progress every 100 reviews
                            logger.info(f"Processed {processed_count}/{total_reviews} reviews...")
                            self.conn.commit() # Commit periodically

                    except Exception as e:
                        logger.error(f"Error processing review_id {review_id}: {e}")
                        self.conn.rollback() # Rollback the transaction for this review
                        # Optionally re-raise or continue
                        continue

                self.conn.commit() # Final commit
                logger.info(f"Finished processing and updating {processed_count} reviews.")

        except ImportError as e:
             logger.error(f"Failed to import TextAnalysis: {e}. Make sure system_code.core is in the Python path.")
        except Exception as e:
            logger.error(f"An error occurred during review processing: {e}")
            self.conn.rollback() # Rollback any pending changes if a major error occurs

    def close(self):
        self.conn.close()

    def database_validation(self):
        db_name = self.config.postgresql['database']
        try:
            # Connect to the default 'postgres' database to check existence/create the target database
            conn_postgres = psycopg2.connect(
                host=self.config.postgresql['host'],
                user=self.config.postgresql['user'],
                password=self.config.postgresql['password'],
                port=self.config.postgresql['port'],
                database='postgres'
            )
            conn_postgres.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn_postgres.cursor() as cursor:
                # Check if the database exists
                cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), (db_name,))
                exists = cursor.fetchone()
                if not exists:
                    # Create database if it does not exist
                    logger.info(f"Database '{db_name}' not found. Creating...")
                    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name)))
                    logger.info(f"Database '{db_name}' created successfully.")
                else:
                    logger.info(f"Database '{db_name}' already exists.")

            conn_postgres.close()

            # Now connect to the target database (self.conn should be connected here from __init__)
            # Ensure self.conn is connected to the correct database
            if self.conn.closed or self.conn.info.dbname != db_name:
                if not self.conn.closed:
                    self.conn.close()
                self.conn = psycopg2.connect(
                    host=self.config.postgresql['host'],
                    port=self.config.postgresql['port'],
                    user=self.config.postgresql['user'],
                    password=self.config.postgresql['password'],
                    database=db_name
                )

            # Create table if not exists in the target database
            self.execute('''
                CREATE TABLE IF NOT EXISTS beauty_reviews (
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
            logger.info('[PGClient] Table validation completed')
        except Exception as e:
            logger.error(f'Database validation failed: {str(e)}')
            # Attempt to close the main connection if it was opened and an error occurred
            if hasattr(self, 'conn') and not self.conn.closed:
                self.conn.close()


if __name__ == '__main__':
    client = PGClient()

    # Example usage of the init_reviews function (optional, can be commented out if not needed):
    # csv_files_to_load = [
    #     '/Users/bytedance/Code/InsightReview/system_code/statics/datasets/reviews/csv/All_Beauty_part_4.csv',
    #     '/Users/bytedance/Code/InsightReview/system_code/statics/datasets/reviews/csv/All_Beauty_part_5.csv'
    # ]
    # client.init_reviews(csv_files_to_load)

    client.close()
    logger.info("PGClient finished and connection closed.")