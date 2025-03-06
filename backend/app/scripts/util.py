from pymongo import AsyncMongoClient

from backend.app.constants import MONGO_URL, DATABASE_NAME, OBJECTIVE_RAW_COLLECTION
from backend.app.scripts.db import get_collection


async def get_all_teams(event_key: str = None):
    if event_key is None:
        team_list_raw = await get_collection(OBJECTIVE_RAW_COLLECTION).find({}, {"_id": 0, "team_number": 1}).to_list(None)
    else:
        team_list_raw = await get_collection(OBJECTIVE_RAW_COLLECTION).find({"event_key": event_key}, {"_id": 0, "team_number": 1}).to_list(None)
    # print(team_list_raw)
    team_list = [item["team_number"] for item in team_list_raw]
    team_set = set(team_list)
    # print(team_set)
    if '' in team_set:
        team_set.remove('')

    return team_set
