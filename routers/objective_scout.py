from fastapi import APIRouter, Body, Query
from starlette import status
from typing_extensions import Annotated

from constants import OBJECTIVE_RAW_COLLECTION
from model import ObjectiveMatchRawData  # , MatchRawDataFilterParams
from scripts.initdb import init_collection

objective_raw = init_collection(OBJECTIVE_RAW_COLLECTION) # db[OBJECTIVE_DATA_COLLECTION]

router = APIRouter(
    prefix="/objective",
    tags=["Objective Match Data"]
)

@router.post(
    "/raw",
    name= "Adding objective match data",
    description= "Post a new objective match data in the server database.",
    response_description="Added a new objective match data successfully",
    response_model=ObjectiveMatchRawData,
    status_code=status.HTTP_201_CREATED,
)
async def add_obj_match_data(data: ObjectiveMatchRawData = Body(...)):
    await objective_raw.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "/raw",
    name= "Getting objective match data",
    description="Getting objective match data from the database.",
    response_description="Got objective match data successfully",
    response_model=list[ObjectiveMatchRawData],
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data(data_query: Annotated[ObjectiveMatchRawData, Query()]):
    return data_query

async def get_obj_match_data_by_team(team_number: int):
    data = []
    async for obj in objective_raw.find({"team_number": team_number}):
        data.append(obj)
    return data