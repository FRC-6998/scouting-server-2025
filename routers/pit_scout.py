from fastapi import APIRouter, Body
from fastapi.params import Query
from pymongo import AsyncMongoClient
from starlette import status
from typing_extensions import Annotated

from constants import DATABASE_NAME, MONGO_URL, PIT_DATA_COLLECTION
from model import PitScoutData

router = APIRouter(
    prefix="/pit_scout",
    tags=["Pit Scout Data"]
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
    "",
    name="Getting pit scout data by team number",
    description="Getting pit scout data filtered by team number from the database.",
    response_description="Got pit scout data filtered by team number successfully",
    response_model=PitScoutData,
    status_code=status.HTTP_200_OK,
)
async def get_pit_scout_data(data_query: Annotated[PitScoutData, Query()]):
    return data_query