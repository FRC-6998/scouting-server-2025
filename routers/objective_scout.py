from fastapi import APIRouter, Body
from pymongo import AsyncMongoClient
from starlette import status

from model import ObjectiveMatchData

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

router = APIRouter(prefix='/objective_scout')
client = AsyncMongoClient("localhost", 27017)
db = client[DATABASE_NAME]
raw_collection = db["raw_data"]

@router.post(
    "",
    response_description="Add a new objective match data",
    response_model=ObjectiveMatchData,
    status_code=status.HTTP_201_CREATED,
)
async def add_obj_match_data(data: ObjectiveMatchData = Body(...)):
    await raw_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "",
    response_description="Get all objective match data",
    response_model=list[ObjectiveMatchData],
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data():
    data = []
    async for obj in raw_collection.find():
        data.append(obj)
    return data

@router.get(
    "",
    response_description="Get match data filtered by match level and number",
    response_model=ObjectiveMatchData,
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data_by_match(match_type: str, match_number: int):
    data = []
    async for obj in raw_collection.find({"match_type": match_type, "match_number": match_number}):
        data.append(obj)
    return data