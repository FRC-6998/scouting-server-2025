from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import objective_scout, subjective_scout, pit_scout, test
from .scripts.objective_calculate import raw_collection

scouting_app = FastAPI(
    title="Scouting Field Server API",
    description="API for Scouting Field Server made by Team Unipards 6998",
    version="0.2.0-alpha",
)


origins = [
    "http://localhost:52695",
]

scouting_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scouting_app.include_router(objective_scout.router)
scouting_app.include_router(subjective_scout.router)
scouting_app.include_router(pit_scout.router)
scouting_app.include_router(test.router)


@scouting_app.get(
    "/team_list",
    name="Getting team list",
    description="Getting team list from the database.",
    response_description="Got team list successfully",
)
async def get_team_list(event_key: str = None):
    if event_key is None:
        team_list_raw = await raw_collection.find({}, {"_id": 0, "team_number": 1}).to_list(None)
    else:
        team_list_raw = await raw_collection.find({"event_key": event_key}, {"_id": 0, "team_number": 1}).to_list(None)
    # print(team_list_raw)
    team_list = [item["team_number"] for item in team_list_raw]
    team_set = set(team_list)
    # print(team_set)
    if '' in team_set:
        team_set.remove('')

    return team_set


@scouting_app.get("/refresh_result")
async def refresh_result():
    await test.refresh_all_obj_results()
    return {"message": "Result refreshed successfully"}
