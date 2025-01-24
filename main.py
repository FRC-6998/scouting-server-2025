from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

app = FastAPI()

# MongoDB connection setting
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "scouting-field"

# Generate MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
