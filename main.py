# TODO: Make every model have its own ulid field.

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from routers import objective_scout, subjective_scout

scouting_app = FastAPI(
    title="Scouting Field Server API",
    description="API for Scouting Field Server made by Team Unipards 6998",
    version="0.1.0",
)

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncMongoClient("localhost", 27017)
db = client[DATABASE_NAME]
test_collection = db["test"]
raw_collection = db["raw_data"]

# OBJECTIVE MATCH DATA
# Utilities

# Test Only
# @scouting_app.post(
#     "/TestData",
#     response_description='Add a new test data',
#     response_model=TestModel,
#     status_code=status.HTTP_201_CREATED
# )
# async def add_test_data(data: TestModel = Body(...)):
#     await test_collection.insert_one(data.model_dump(), bypass_document_validation=False, session=None)
#     return data

scouting_app.include_router(objective_scout.router)
scouting_app.include_router(subjective_scout.router)