from pymongo import AsyncMongoClient
import aiohttp

from ..constants import MONGO_URL, DATABASE_NAME, OBJECTIVE_RAW_COLLECTION
from ..scripts.db import get_collection


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


async def post_to_remote_server(data: dict, ulid: str, remote_server: str, remote_path: str, collection_name: str):
    remote_url = f"{remote_server}{remote_path}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(remote_url, json=data) as response:
                if response.status >= 200 and response.status < 300:
                    print(f"Data sent to {remote_url} successfully")
                    await get_collection(collection_name).update_one(
                        {"ulid": ulid}, {"$push": {"uploaded_remote": remote_server}})
                elif response.status == 409:
                    print(f"Data already exists in {remote_url}")
                    await get_collection(collection_name).update_one(
                        {"ulid": ulid}, {"$push": {"uploaded_remote": remote_server}})
                else:
                    print(f"Failed to send data to {remote_url} with status code {response.status} and response text: {await response.text()}")
    except aiohttp.ClientConnectorError as e:
        print(f"Failed to connect to {remote_url} with error: {e}")
    except Exception as e:
        print(f"Failed to send data to {remote_url} with error: {e}")
