from typing import List, Optional, Annotated, Literal
from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import BaseModel, Field
from ulid import ULID

# Objective Match Data (formerly known as Scouting Data)

# Match basic information

class MatchType (str, Enum):
    PRACTICE = "Practice"
    QUALIFICATION = "Qualification"
    PLAYOFF = "Playoff"

class Alliance (str, Enum):
    RED = "Red"
    BLUE = "Blue"

# Auto

class Preload (str, Enum):
    NONE = "None"
    CORAL = "Coral"
    ALGAE = "Algae"

class AutoStartPosition(str, Enum):
    SIDE = "Side"
    CENTER = "Center"
    MIDDLE = "Middle"

class AutoPathPosition (str, Enum):
    # Coral Station
    LEFT_CORAL_STATION = "leftCoralStation"
    RIGHT_CORAL_STATION = "rightCoralStation"
    # Ground
    LEFT_GROUND_CORAL = "leftGroundCoral"
    CENTER_GROUND_CORAL = "centerGroundCoral"
    RIGHT_GROUND_CORAL = "rightGroundCoral"
    LEFT_GROUND_ALGAE = "leftGroundAlgae"
    CENTER_GROUND_ALGAE = "centerGroundAlgae"
    RIGHT_GROUND_ALGAE = "rightGroundAlgae"
    # Reef
    L1_REEF_AB = "l1ReefAB"
    L1_REEF_CD = "l1ReefCD"
    L1_REEF_EF = "l1ReefEF"
    L1_REEF_GH = "l1ReefGH"
    L1_REEF_IJ = "l1ReefIJ"
    L1_REEF_KL = "l1ReefKL"
    L2_REEF_AB = "l2ReefAB"
    L2_REEF_CD = "l2ReefCD"
    L2_REEF_EF = "l2ReefEF"
    L2_REEF_GH = "l2ReefGH"
    L2_REEF_IJ = "l2ReefIJ"
    L2_REEF_KL = "l2ReefKL"
    L3_REEF_AB = "l3ReefAB"
    L3_REEF_CD = "l3ReefCD"
    L3_REEF_EF = "l3ReefEF"
    L3_REEF_GH = "l3ReefGH"
    L3_REEF_IJ = "l3ReefIJ"
    L3_REEF_KL = "l3ReefKL"
    L4_REEF_AB = "l4ReefAB"
    L4_REEF_CD = "l4ReefCD"
    L4_REEF_EF = "l4ReefEF"
    L4_REEF_GH = "l4ReefGH"
    L4_REEF_IJ = "l4ReefIJ"
    L4_REEF_KL = "l4ReefKL"

class AutoPath (BaseModel):
    second: float = Field(10.0)
    position: str = Field("None")
    success: bool = False

class AutoRaw (BaseModel):
    preload: Preload = "None"
    start_position: AutoStartPosition
    leave: bool = False
    auto_path: List[AutoPath]

# Teleop

class TeleopPath (BaseModel):
    second: float
    position: str
    success: bool = False

class TeleopRaw (BaseModel):
    teleop_path: List[TeleopPath]

# Endgame

class BargeAction (str, Enum):
    NONE = "None"
    PARK = "Park"
    DEEP = "Deep"
    SHALLOW = "Shallow"

# General Model

class ObjectiveMatchRawData (BaseModel):
    # "_id" field: Making sure that the data in temp and db has same id
    ulid: ULID = None
    scout: str = None
    match_type: MatchType = None
    match_number: int = None
    event_key: str = None
    team_number: int = None
    alliance: Alliance = None
    auto : AutoRaw = None
    teleop: TeleopRaw = None
    barge_action: BargeAction = None
    barge_time: float = None

# Subjective Match Data (formerly known as Super Scout Data)

class SubjectiveRanking3 (IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class SubjectiveRanking2 (IntEnum):
    FIRST = 1
    SECOND = 2

class SubjectiveMatchRawData (BaseModel):
    ulid: ULID = None
    scout: str = None
    match_type: MatchType = None
    match_number: int = None
    event_key: str = None
    team_number: int = None
    alliance: Alliance = None
    driver_awareness: SubjectiveRanking3 = None
    coral_station_awareness: SubjectiveRanking2 = None
    num_score_on_net: int = None
    mobility: SubjectiveRanking3 = None
    defense: SubjectiveRanking3 = None

# Pit Scout Data

class Chassis (str, Enum):
    SWERVE = "Swerve"
    MECANUM = "Mecanum"
    TANK = "Tank"

class MainSuperstructure (str, Enum):
    ARM = "Arm"
    ELEVATOR = "Elevator"

class IntakeType (str, Enum):
    INTEGRATED = "Integrated"
    SEPERATED = "Seperated"

class AlgaeScoringCapabilityChoice (str, Enum):
    PROCESSOR = "Processor"
    NET = "Net"

class ReefCapabilityChoice (str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"

class PreloadChoice (str, Enum):
    CORAL = "Coral"
    ALGAE = "Algae"

class BargeCapabilityChoice (str, Enum):
    PARK = "Park"
    DEEP = "Deep"
    SHALLOW = "Shallow"

class VisionFunctionalityChoice (str, Enum):
    AUTO_ALIGN = "Auto Align"
    FIELD_RELATED_POS = "Field-Related Positioning"
    OBJ_DETECT = "Object Detection"

class PitScoutData (BaseModel):
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

# Data filter query params

# TODO: Add analysis data return model.