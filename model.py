# TODO: Make sure all the parameters are suitable to the requirement driver teams provided.

from uuid import uuid4
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, PrivateAttr, computed_field


# Match type enum
class MatchType(str, Enum):
    PRACTICE = "Practice"
    QUALIFICATION = "Qualification"
    PLAYOFF = "Playoff"

# Model to verify input data
class ObjectiveMatchData(BaseModel):

    # "_id" field: Making sure that the data in temp and db has same id
    _id: UUID = PrivateAttr(default_factory= lambda: uuid4())
    @computed_field
    @property
    def data_id(self) -> UUID:
        return self._id

    match_type: MatchType
    match_number: int
    team_number: int