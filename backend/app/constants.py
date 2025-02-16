from os import getenv
# MongoDB connection setting

MONGO_HOST = getenv("MONGO_HOST", "localhost")
MONGO_PORT = getenv("MONGO_PORT", "27017")
MONGO_URL = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
DATABASE_NAME = "scouting-field"

# MongoDB Collections
OBJECTIVE_RAW_COLLECTION = "objective_raw"
SUBJECTIVE_RAW_COLLECTION = "subjective_raw"
OBJECTIVE_RESULT_COLLECTION = "objective_result"
SUBJECTIVE_RESULT_COLLECTION = "subjective_result"
PIT_DATA_COLLECTION = "pit"