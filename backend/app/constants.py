from os import getenv
# MongoDB connection setting

MONGO_HOST = getenv("MONGO_HOST", "localhost")
MONGO_URL = "mongodb://db:27017"
DATABASE_NAME = "scouting-field"

TEST_MONGO_URL = "mongodb://localhost:27017"
TEST_DATABASE_NAME = "scouting-field"

# MongoDB Collections
OBJECTIVE_RAW_COLLECTION = "objective_raw"
SUBJECTIVE_RAW_COLLECTION = "subjective_raw"
OBJECTIVE_RESULT_COLLECTION = "objective_result"
SUBJECTIVE_RESULT_COLLECTION = "subjective_result"
PIT_DATA_COLLECTION = "pit"