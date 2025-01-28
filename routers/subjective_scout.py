from fastapi import APIRouter, Body
from pymongo import AsyncMongoClient
from starlette import status

from model import SubjectiveMatchData

MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

client = AsyncMongoClient("localhost", 27017)
db = client[DATABASE_NAME]
subjective_collection = db["subjective"]

router = APIRouter(
    prefix="/subjective",
    tags=["subjective match data"]
)

@router.post(
    "",
    name= "Adding subjective match data",
    description= "Post a new objective match data in the server database.",
    response_description="Added a new objective match data successfully",
    response_model=SubjectiveMatchData,
    status_code=status.HTTP_201_CREATED,
)
async def add_sbj_match_data(data: SubjectiveMatchData = Body(...)):
    await subjective_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "/get/all",
    name= "Getting all subjective match data",
    description="Getting all subjective match data from the database.",
    response_description="Got all subjective match data successfully",
    response_model=list[SubjectiveMatchData],
    status_code=status.HTTP_200_OK,
)
async def get_sbj_match_data():
    data = []
    async for sbj in subjective_collection.find():
        data.append(sbj)
    return data

@router.get(
    "/get",
    name="Getting subjective match data by match type and number",
    description="Getting subjective match data filtered by match level and number from the database.",
    response_description="Got subjective match data filtered by match level and number successfully",
    response_model=SubjectiveMatchData,
    status_code=status.HTTP_200_OK,
)
async def get_sub_match_data_by_match(match_type: str, match_number: int):
    data = []
    async for sbj in subjective_collection.find({"match_type": match_type, "match_number": match_number}):
        data.append(sbj)
    return data