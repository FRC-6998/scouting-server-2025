from fastapi import APIRouter
from pymongo import AsyncMongoClient

from constants import MONGO_URL, DATABASE_NAME, RESULT_DATA_COLLECTION

router = APIRouter(
    prefix= "/result",
    tags= ["Results"]
)

client = AsyncMongoClient(MONGO_URL)
db = client[DATABASE_NAME]
collection = db[RESULT_DATA_COLLECTION]

