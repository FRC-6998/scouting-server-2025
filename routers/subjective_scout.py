from fastapi import APIRouter, Body
from pymongo import AsyncMongoClient
from starlette import status

from constants import DATABASE_NAME, MONGO_URL, SUBJECTIVE_DATA_COLLECTION
from model import SubjectiveMatchData

client = AsyncMongoClient(MONGO_URL)
db = client[DATABASE_NAME]
subjective_collection = db[SUBJECTIVE_DATA_COLLECTION]

router = APIRouter(
    prefix="/subjective",
    tags=["subjective match data"]
)

@router.post(
    "",
    name= "Adding subjective match data",
    description= "Post a new subjective match data in the server database.",
    response_description="Added a new subjective match data successfully",
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
    "/get/match",
    name="Getting subjective match data by match type and number",
    description="Getting subjective match data filtered by match level and number from the database.",
    response_description="Got subjective match data filtered by match level and number successfully",
    response_model=SubjectiveMatchData,
    status_code=status.HTTP_200_OK,
)
async def get_sbj_match_data_by_match(match_type: str, match_number: int):
    data = []
    async for sbj in subjective_collection.find({"match_type": match_type, "match_number": match_number}):
        data.append(sbj)
    return data