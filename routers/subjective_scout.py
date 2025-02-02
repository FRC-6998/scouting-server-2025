from fastapi import APIRouter, Body
from fastapi.params import Query
from starlette import status
from typing_extensions import Annotated

from constants import SUBJECTIVE_DATA_COLLECTION
from model import SubjectiveMatchRawData  # , MatchRawDataFilterParams
from scripts.initdb import init_collection

subjective_collection = init_collection(SUBJECTIVE_DATA_COLLECTION)

router = APIRouter(
    prefix="/subjective",
    tags=["Subjective Match Data"]
)

@router.post(
    "",
    name= "Adding subjective match data",
    description= "Post a new subjective match data in the server database.",
    response_description="Added a new subjective match data successfully",
    response_model=SubjectiveMatchRawData,
    status_code=status.HTTP_201_CREATED,
)
async def add_sbj_match_data(data: SubjectiveMatchRawData = Body(...)):
    await subjective_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    return data

@router.get(
    "",
    name= "Getting subjective match data",
    description="Getting subjective match data from the database.",
    response_description="Got subjective match data successfully",
    response_model=list[SubjectiveMatchRawData],
    status_code=status.HTTP_200_OK,
)
async def get_sbj_match_data(data_query: Annotated[SubjectiveMatchRawData, Query()]):
    return data_query