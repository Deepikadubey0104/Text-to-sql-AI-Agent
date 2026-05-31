import psycopg2
from dotenv import load_dotenv
import os
from config.logger import logger

load_dotenv()

def get_postgres_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        )
        logger.info("Postgres connected successfully!")
        return connection
    except Exception as e:
        logger.error(f"Postgres connection failed: {e}")
        raise


def execute_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        logger.info(f"Query executed successfully: {query}")
        return {"columns": columns, "rows": rows}
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise


def disconnect(connection):
    if connection:
        connection.close()
        logger.info("Postgres disconnected.")