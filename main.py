from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.params import Body

scouting_app = FastAPI()

# Temporarily data list
match_data_temp = []

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

@scouting_app.post("/postMatchTempData")
async def post_match_temp_data(team_data: dict = Body(...)):
    match_data_temp.append(team_data)
    return {
        "message":
            "Match data has saved to temporary list. Please verify it and save it to the database later."
    }

@scouting_app.get("/getMatchTempData")
async def get_match_temp_data():
    return match_data_temp
