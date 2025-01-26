from uuid import UUID
from enum import Enum
from fastapi import FastAPI, responses, HTTPException, status
from fastapi.params import Body
from pymongo import MongoClient, AsyncMongoClient

from model import *
from pydantic import BaseModel
import pymongo

scouting_app = FastAPI()

# Temporarily data methods
match_data_temp = []

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncMongoClient("localhost", 27017)
db = client[DATABASE_NAME]
raw_collection = db["raw_data"]

# OBJECTIVE MATCH DATA
# Utilities

def find_match_data(finding_uuid: UUID):
    for match in match_data_temp:
        if match.match_uuid == finding_uuid:
            return match

def delete_match_data(finding_uuid: UUID):
    for match in match_data_temp:
        if match.match_uuid == finding_uuid:
            match_data_temp.remove(match)
