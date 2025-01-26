from uuid import uuid4
from enum import Enum
from typing import List

from ulid import ULID

from pydantic import BaseModel, PrivateAttr, computed_field

# Objective Match Data (formerly known as Scouting Data)

# Match basic information

class MatchType(str, Enum):
    PRACTICE = "Practice"
    QUALIFICATION = "Qualification"
    PLAYOFF = "Playoff"

class Alliance(str, Enum):
    RED = "Red"
    BLUE = "Blue"

# Auto

class Preload(str, Enum):
    NONE = "None"
    CORAL = "Coral"
    ALGAE = "Algae"

class AutoStartPosition(str, Enum):
    SIDE = "Side"
    CENTER = "Center"
    MIDDLE = "Middle"

class AutoPathPosition(str, Enum):
    # TODO: List out all possible positions
    EXAMPLE = "Example"

class AutoPath(BaseModel):
    second: float
    position: str
    success: bool = False

class Auto(BaseModel):
    preload: Preload = "None"
    start_position: AutoStartPosition
    leave: bool = False
    auto_path: List[AutoPath]

# Teleop

class TeleopPath(BaseModel):
    second: float
    position: str
    success: bool = False

class Teleop(BaseModel):
    teleop_path: List[TeleopPath]

# Endgame

class BargeAction(str, Enum):
    NONE = "None"
    PARK = "Park"
    DEEP = "Deep"
    SHALLOW = "Shallow"

# Objective Match Data Model

class ObjectiveMatchData(BaseModel):
    # "_id" field: Making sure that the data in temp and db has same id
    _id: ULID
    scout: str
    match_type: MatchType
    match_number: int
    event_key: str
    team_number: int
    alliance: Alliance
    auto : Auto
    teleop: Teleop
    barge_action: BargeAction
    barge_time: float