import asyncio

from fastapi import APIRouter, Query, BackgroundTasks
from starlette import status
from typing_extensions import Annotated

from ..constants import OBJECTIVE_RAW_COLLECTION, OBJECTIVE_RESULT_COLLECTION
from ..model import ObjectiveMatchRawData, ObjectiveResult  # , MatchRawDataFilterParams
from ..scripts.objective_calculate import post_obj_results, pack_obj_data_abs, refresh_all_obj_results
from ..scripts.subjective_calculate import pack_result
from ..scripts.util import init_collection

# db[OBJECTIVE_DATA_COLLECTION]
objective_raw = init_collection(OBJECTIVE_RAW_COLLECTION)
# db[OBJECTIVE_RESULT_COLLECTION]
objective_result = init_collection(OBJECTIVE_RESULT_COLLECTION)

router = APIRouter(
    prefix="/objective",
    tags=["Objective Match Data"]
)


@router.post(
    "/raw",
    name="Adding objective match data",
    description="Post a new objective match data in the server database.",
    response_description="Added a new objective match data successfully",
    status_code=status.HTTP_201_CREATED,
)
async def add_obj_match_data(data: ObjectiveMatchRawData, background_tasks: BackgroundTasks):
    await objective_raw.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
    background_tasks.add_task(refresh_all_obj_results)
    return {"message": "Data added successfully"}


@router.get(
    "/raw",
    name="Getting objective match data",
    description="Getting objective match data from the database.",
    response_description="Got objective match data successfully",
    response_model=list[ObjectiveMatchRawData],
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_data(data_query: Annotated[ObjectiveMatchRawData, Query()]):
    return data_query


@router.delete(
    "/raw/{match_id}",
    name="Deleting objective match data",
    description="Deleting objective match data from the database.",
    response_description="Deleted objective match data successfully",
    response_model=ObjectiveMatchRawData,
    status_code=status.HTTP_200_OK,
)
async def delete_obj_match_data(match_id: str):
    await objective_raw.delete_one({"match_id": match_id})
    return {"message": "Data with id [" + match_id + "] deleted successfully"}

@router.get(
    "/result",
    name="Getting objective match results",
    description="Getting objective match results from the database.",
    response_description="Got objective match results successfully",
    response_model=ObjectiveResult,
    status_code=status.HTTP_200_OK,
)
async def get_obj_match_results(team_number: str):
    data = await objective_result.find_one({"team_number": team_number},{"_id": 0})
    print (data)
    return data