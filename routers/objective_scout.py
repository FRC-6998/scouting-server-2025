from fastapi import APIRouter, Body
from pymongo import AsyncMongoClient
from starlette import status
from constants import MONGO_URL, DATABASE_NAME, OBJECTIVE_DATA_COLLECTION
from model import ObjectiveMatchData

client = AsyncMongoClient(MONGO_URL)
db = client[DATABASE_NAME]
objective_collection = db[OBJECTIVE_DATA_COLLECTION]

router = APIRouter(
    prefix="/objective",
    tags=["objective match data"]
)

@router.post(
    "",
    name= "Adding objective match data",
    description= "Post a new objective match data in the server database.",
    response_description="Added a new objective match data successfully",
    response_model=ObjectiveMatchData,
    status_code=status.HTTP_201_CREATED,
)
async def add_obj_match_data(data: ObjectiveMatchData = Body(...)):
    await objective_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "/get/all",
    name= "Getting all objective match data",
    description="Getting all objective match data from the database.",
    response_description="Got all objective match data successfully",
    response_model=list[ObjectiveMatchData],
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data():
    data = []
    async for obj in objective_collection.find():
        data.append(obj)
    return data

@router.get(
    "/get",
    name="Getting objective match data by match type and number",
    description="Getting objective match data filtered by match level and number from the database.",
    response_description="Got objective match data filtered by match level and number successfully",
    response_model=ObjectiveMatchData,
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data_by_match(match_type: str, match_number: int):
    data = []
    async for obj in objective_collection.find({"match_type": match_type, "match_number": match_number}):
        data.append(obj)
    return data