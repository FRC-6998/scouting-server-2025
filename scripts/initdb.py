from pymongo import AsyncMongoClient

from constants import MONGO_URL, DATABASE_NAME


def init_collection (collection_name: str):
    client = AsyncMongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    collection = db[collection_name]
    return collection