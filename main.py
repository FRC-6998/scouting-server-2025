import uuid
from enum import Enum
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.params import Body
from model import ObjectiveMatchData
from pydantic import BaseModel

scouting_app = FastAPI()

# Temporarily data list
match_data_temp = []

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

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
