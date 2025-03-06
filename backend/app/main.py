from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.scripts.db import get_collection, init_db, disconnect_from_mongo
from backend.app.constants import OBJECTIVE_RAW_COLLECTION

from .routers import objective_scout, subjective_scout, pit_scout, test

scouting_app = FastAPI(
    title="Scouting Field Server API",
    description="API for Scouting Field Server made by Team Unipards 6998",
    version="0.2.0-alpha",
)


origins = [
    "http://localhost:8080",
    "https://eran0926.github.io"
]

scouting_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@scouting_app.on_event("startup")
async def startup():
    await init_db()


@scouting_app.on_event("shutdown")
async def shutdown():
    await disconnect_from_mongo()


@scouting_app.exception_handler(Exception)
async def exception_handler(request, exc):
    headers = {
        'Access-Control-Allow-Origin': ', '.join(origins),
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': '*',
        'Access-Control-Allow-Headers': '*',
    }
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
        headers=headers
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


@scouting_app.get("/refresh_result")
async def refresh_result():
    await test.refresh_all_obj_results()
    return {"message": "Result refreshed successfully"}
