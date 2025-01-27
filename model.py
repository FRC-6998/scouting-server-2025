from enum import Enum
from typing import List

from pydantic import BaseModel
from ulid import ULID


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

# General Model

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

# Subjective Match Data (formerly known as Super Scout Data)

class SubjectiveRanking3(int, Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class SubjectiveRanking2(int, Enum):
    FIRST = 1
    SECOND = 2

class SubjectiveMatchData(BaseModel):
    _id: ULID
    scout: str
    match_type: MatchType
    match_number: int
    event_key: str
    team_number: int
    alliance: Alliance
    driver_awareness: SubjectiveRanking3
    coral_station_awareness: SubjectiveRanking2
    num_score_on_net: int
    mobility = SubjectiveRanking3
    defense = SubjectiveRanking3