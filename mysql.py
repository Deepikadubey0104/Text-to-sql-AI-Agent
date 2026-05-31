import pymysql
import os
from dotenv import load_dotenv
from config.logger import logger

load_dotenv()


def get_mysql_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT")),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info("MySQL connected successfully!")
        return connection
    except Exception as e:
        logger.error(f"MySQL connection failed: {e}")
        raise


def execute_mysql_query(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        rows_raw = cursor.fetchall()
        if not rows_raw:
            return {"columns": [], "rows": []}
        columns = list(rows_raw[0].keys())
        rows = [tuple(row.values()) for row in rows_raw]
        cursor.close()
        logger.info(f"MySQL query executed successfully: {query}")
        return {"columns": columns, "rows": rows}
    except Exception as e:
        logger.error(f"MySQL query execution failed: {e}")
        raise


def disconnect_mysql(connection):
    if connection:
        connection.close()
        logger.info("MySQL disconnected.")