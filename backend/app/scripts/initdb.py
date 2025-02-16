from pymongo import AsyncMongoClient

from ..constants import MONGO_URL, DATABASE_NAME, TEST_MONGO_URL


def init_collection(collection_name: str):
    print(f"Connecting to {MONGO_URL} and {DATABASE_NAME}")
    client = AsyncMongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    return collection
