from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import BaseModel
from ulid import ULID

# Model which are only made for testing
class TestModel(BaseModel):
    _id: ULID
    name: str

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
    ulid: ULID
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

class SubjectiveRanking3(IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class SubjectiveRanking2(IntEnum):
    FIRST = 1
    SECOND = 2

class SubjectiveMatchData(BaseModel):
    ulid: ULID
    scout: str
    match_type: MatchType
    match_number: int
    event_key: str
    team_number: int
    alliance: Alliance
    driver_awareness: SubjectiveRanking3
    coral_station_awareness: SubjectiveRanking2
    num_score_on_net: int
    mobility: SubjectiveRanking3
    defense: SubjectiveRanking3

# Pit Scout Data

class Chassis(str, Enum):
    SWERVE = "Swerve"
    MECANUM = "Mecanum"
    TANK = "Tank"

class MainSuperstructure(str, Enum):
    ARM = "Arm"
    ELEVATOR = "Elevator"

class IntakeType(str, Enum):
    INTEGRATED = "Integrated"
    SEPERATED = "Seperated"

class AlgaeScoringCapabilityChoice(str, Enum):
    PROCESSOR = "Processor"
    NET = "Net"

class ReefCapabilityChoice(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"

class PreloadChoice(str, Enum):
    CORAL = "Coral"
    ALGAE = "Algae"

class BargeCapabilityChoice(str, Enum):
    PARK = "Park"
    DEEP = "Deep"
    SHALLOW = "Shallow"

class VisionFunctionalityChoice(str, Enum):
    AUTO_ALIGN = "Auto Align"
    FIELD_RELATED_POS = "Field-Related Positioning"
    OBJ_DETECT = "Object Detection"

class PitScoutData(BaseModel):
    ulid: ULID
    scout: str
    chassis: Chassis
    main_superstructure: MainSuperstructure
    intake_type: IntakeType
    algae_scoring_capability: List[AlgaeScoringCapabilityChoice]
    reef_capability: List[ReefCapabilityChoice]
    preload: Optional[List[PreloadChoice]]
    vision_functionality: Optional[List[VisionFunctionalityChoice]]
    barge_capability: Optional[List[BargeCapabilityChoice]]
    net_confidence: bool
    driver_seniority: int

# TODO: Add analysis data return model.