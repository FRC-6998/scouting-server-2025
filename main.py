import uuid
from enum import Enum
from fastapi import FastAPI, responses, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.params import Body
from model import *
from pydantic import BaseModel

scouting_app = FastAPI()

# Temporarily data methods
match_data_temp = []

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# OBJECTIVE MATCH DATA
# Utilities

def find_match_data(finding_uuid: uuid.UUID):
    for match in match_data_temp:
        if match.match_uuid == finding_uuid:
            return match

def delete_match_data(finding_uuid: uuid.UUID):
    for match in match_data_temp:
        if match.match_uuid == finding_uuid:
            match_data_temp.remove(match)

# Temp file

@scouting_app.post("/postObjectiveMatchTempData")
async def post_objective_match_temp_data(obj_data: ObjectiveMatchData):
    match_data_temp.append(obj_data)
    return {
        "message":
            "Match data has saved to temporary list. Please verify it and save it to the database later."
    }

@scouting_app.get("/getObjectiveMatchTempData")
async def get_objective_match_temp_data():
    return match_data_temp

@scouting_app.get("/getObjectiveMatchTempData/{match_uuid}")
async def get_objective_match_temp_data_by_uuid(match_uuid: uuid.UUID):
    result = find_match_data(match_uuid)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match data not found.")
    return result

@scouting_app.delete("/deleteObjectiveMatchTempData/{match_uuid}")
async def delete_objective_match_temp_data_by_uuid(match_uuid: uuid.UUID):
    for match in match_data_temp:
        if match.match_uuid == match_uuid:
            match_data_temp.remove(match)
            return {
                "message":
                    f"Specified match temp data (UUID: {match_uuid}) has been deleted from list."
            }

# Save data to the db
# @scouting_app.get("/saveObjectiveMatchData")
# async def save_objective_match_data():
#     for match in match_data_temp:
#         await db.objective_match_data.insert_one(match.dict())
#     return {
#         "message":
#             "All match data has been saved to the database. You can now delete the temporary list."
#     }