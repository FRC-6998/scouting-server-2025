from pymongo import AsyncMongoClient
from ..constants import (MONGO_URL,
                         DATABASE_NAME,
                         OBJECTIVE_RAW_COLLECTION,
                         OBJECTIVE_RESULT_COLLECTION,
                         SUBJECTIVE_RAW_COLLECTION,
                         SUBJECTIVE_RESULT_COLLECTION,
                         PIT_DATA_COLLECTION
                         )

client: AsyncMongoClient = None
db = None


async def connect_to_mongo():
    global client, db
    client = AsyncMongoClient(MONGO_URL)
    db = client[DATABASE_NAME]
    print(f"Connected to {MONGO_URL} and {DATABASE_NAME}")
    return db


async def disconnect_from_mongo():
    global client
    if client is not None:
        await client.close()
        print("Disconnected from MongoDB.")


async def check_collection_exist():
    existing_collections = await db.list_collection_names()
    required_collections = [OBJECTIVE_RAW_COLLECTION,
                            OBJECTIVE_RESULT_COLLECTION,
                            SUBJECTIVE_RAW_COLLECTION,
                            SUBJECTIVE_RESULT_COLLECTION,
                            PIT_DATA_COLLECTION]
    for collection in required_collections:
        if collection not in existing_collections:
            await db.create_collection(collection)
            print(f"Collection {collection} created.")
        else:
            print(f"Collection {collection} exists.")


async def ckeck_and_create_index():
    await db[OBJECTIVE_RAW_COLLECTION].create_index("ulid", unique=True)


async def init_db():
    await connect_to_mongo()
    await check_collection_exist()
    await ckeck_and_create_index()


def get_db():
    if db is None:
        print("DB is None")
        raise RuntimeError("DB is not initialized.")
        # await init_db()
    return db


def get_collection(collection_name: str):
    return get_db()[collection_name]
