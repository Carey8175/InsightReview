# -*- coding: utf-8 -*-
import sys
import os

# Add project root to Python path to allow imports like system_code.server.database
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from system_code.server.database.postgres_client import PGClient
from system_code.core.config import logger

def main():
    """Initializes PGClient, runs the review processing, and closes the connection."""
    pg_client = None # Initialize to None
    try:
        logger.info("Initializing database client...")
        pg_client = PGClient()
        logger.info("Starting review processing...")
        pg_client.process_and_update_reviews()
        logger.info("Review processing finished.")
    except Exception as e:
        logger.error(f"An error occurred during the process: {e}")
    finally:
        if pg_client:
            logger.info("Closing database connection...")
            pg_client.close()
            logger.info("Database connection closed.")

if __name__ == "__main__":
    main()