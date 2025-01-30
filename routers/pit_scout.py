from fastapi import APIRouter, Body
from pymongo import AsyncMongoClient
from starlette import status

from constants import DATABASE_NAME, MONGO_URL, PIT_DATA_COLLECTION
from model import PitScoutData

router = APIRouter(
    prefix="/pit_scout",
    tags=["pit scout data"]
)

client = AsyncMongoClient(MONGO_URL)
db = client[DATABASE_NAME]
pit_collection = db[PIT_DATA_COLLECTION]

@router.post(
    "",
    name= "Adding pit scout data",
    description= "Post a new pit scout data in the server database.",
    response_description="Added a new pit scout data successfully",
    response_model=PitScoutData,
    status_code=status.HTTP_201_CREATED,
)
async def add_pit_scout_data(data: PitScoutData = Body(...)):
    await pit_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "/get/all",
    name= "Getting all pit scout data",
    description="Getting all pit scout data from the database.",
    response_description="Got all pit scout data successfully",
    response_model=list[PitScoutData],
    status_code=status.HTTP_200_OK,
)
async def get_pit_scout_data():
    data = []
    async for sbj in pit_collection.find():
        data.append(sbj)
    return data

@router.get(
    "/get/match",
    name="Getting pit scout data by match type and number",
    description="Getting pit scout data filtered by match level and number from the database.",
    response_description="Got pit scout data filtered by match level and number successfully",
    response_model=PitScoutData,
    status_code=status.HTTP_200_OK,
)
async def get_pit_scout_data_by_match(match_type: str, match_number: int):
    data = []
    async for sbj in pit_collection.find({"match_type": match_type, "match_number": match_number}):
        data.append(sbj)
    return data

@router.get(
    "/get/team",
    name="Getting pit scout data by team number",
    description="Getting pit scout data filtered by team number from the database.",
    response_description="Got pit scout data filtered by team number successfully",
    response_model=PitScoutData,
    status_code=status.HTTP_200_OK,
)
async def get_pit_scout_data_by_team(team_number: int):
    data = []
    async for sbj in pit_collection.find({"team_number": team_number}):
        data.append(sbj)
    return data