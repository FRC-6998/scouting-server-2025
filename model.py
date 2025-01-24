# TODO: Make sure all the parameters are suitable to the requirement driver teams provided.

import uuid
from enum import Enum
from pydantic import BaseModel

# Match type enum
class MatchType(str, Enum):
    PRACTICE = "Practice"
    QUALIFICATION = "Qualification"
    PLAYOFF = "Playoff"

# Model to verify input data
class ObjectiveMatchData(BaseModel):
    match_uuid: uuid.UUID
    match_type: MatchType
    match_number: int
    team_number: int