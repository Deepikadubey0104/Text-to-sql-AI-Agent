import pymongo
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from config.logger import logger

load_dotenv()


def get_mongo_client():
    try:
        username = quote_plus(os.getenv("MONGO_USER"))
        password = quote_plus(os.getenv("MONGO_PASSWORD"))
        uri = f"mongodb://{username}:{password}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
        client = pymongo.MongoClient(uri)
        logger.info("MongoDB connected successfully!")
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise


def get_mongo_database(client):
    return client[os.getenv("MONGO_DATABASE")]


def execute_mongo_query(db, collection_name, query_filter=None, projection=None, limit=100):
    try:
        collection = db[collection_name]
        query_filter = query_filter or {}
        projection = projection or {}
        cursor = collection.find(query_filter, projection).limit(limit)
        rows = list(cursor)

        for row in rows:
            row.pop("_id", None)

        if not rows:
            return {"columns": [], "rows": []}

        columns = list(rows[0].keys())
        result_rows = [tuple(row.values()) for row in rows]
        logger.info(f"MongoDB query executed on collection: {collection_name}")
        return {"columns": columns, "rows": result_rows}
    except Exception as e:
        logger.error(f"MongoDB query execution failed: {e}")
        raise


def disconnect_mongo(client):
    if client:
        client.close()
        logger.info("MongoDB disconnected.")