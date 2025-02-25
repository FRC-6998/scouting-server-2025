from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Query
from starlette import status
from typing_extensions import Annotated

from ..constants import SUBJECTIVE_RAW_COLLECTION
from ..model import SubjectiveMatchRawData  # , MatchRawDataFilterParams
from ..scripts.objective_calculate import post_obj_results
from ..scripts.subjective_calculate import post_sbj_results
from ..scripts.util import init_collection

subjective_collection = init_collection(SUBJECTIVE_RAW_COLLECTION)

router = APIRouter(
    prefix="/subjective",
    tags=["Subjective Match Data"]
)


@router.post(
    "/raw",
    name="Adding subjective match data",
    description="Post a new subjective match data in the server database.",
    response_description="Added a new subjective match data successfully",
    response_model=SubjectiveMatchRawData,
    status_code=status.HTTP_201_CREATED,
)
async def add_sbj_match_data(data: SubjectiveMatchRawData, background_tasks: BackgroundTasks):
    await subjective_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    background_tasks.add_task(post_obj_results, data.team_number)
    return {"message": "Data added successfully"}


@router.get(
    "/raw",
    name="Getting subjective match data",
    description="Getting subjective match data from the database.",
    response_description="Got subjective match data successfully",
    response_model=list[SubjectiveMatchRawData],
    status_code=status.HTTP_200_OK,
)
async def get_sbj_match_data(data_query: Annotated[SubjectiveMatchRawData, Query()]):
    return data_query


@router.delete(
    "/raw/{match_id}",
    name="Deleting subjective match data",
    description="Deleting subjective match data from the database.",
    response_description="Deleted subjective match data successfully",
    response_model=SubjectiveMatchRawData,
    status_code=status.HTTP_200_OK,
)
async def delete_sbj_match_data(match_id: str):
    await subjective_collection.delete_one({"match_id": match_id})
    return {"message": "Data with id [" + match_id + "] deleted successfully"}


@router.get(
    "/result",
    name="Getting subjective match results",
    description="Getting subjective match results from the database.",
    response_description="Got subjective match results successfully",
    response_model=list[SubjectiveMatchRawData],
    status_code=status.HTTP_200_OK,
)
async def get_sbj_match_results(team_number: int):
    await post_sbj_results(team_number)
    return await subjective_collection.find()
