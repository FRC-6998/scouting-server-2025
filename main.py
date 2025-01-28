# TODO: Make every model have its own ulid field.

from pickle import FALSE
from uuid import UUID
from enum import Enum
from fastapi import FastAPI, responses, HTTPException, status
from fastapi.params import Body
from pymongo import MongoClient, AsyncMongoClient
from routers import objective_scout

from model import ObjectiveMatchData, TestModel
from pydantic import BaseModel
import pymongo

scouting_app = FastAPI()

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