from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import BaseModel, Field
from ulid import ULID


# Objective Match Data (formerly known as Scouting Data)

# Match basic information

class MatchLevel (str, Enum):
    UNSET = "unset"
    PRACTICE = "practice"
    QUALIFICATION = "qualification"
    PLAYOFF = "playoff"

class Alliance (str, Enum):
    UNSET = "unset"
    RED = "red"
    BLUE = "blue"

# Auto

class Preload (str, Enum):
    UNSET = "unset"
    NONE = "none"
    CORAL = "coral"
    ALGAE = "algae"

class AutoStartPosition(str, Enum):
    UNSET = "unset"
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class AutoPathPoint (str, Enum):
    LEFT_CORAL_STATION = "leftCoralStation"
    RIGHT_CORAL_STATION = "rightCoralStation"

    LEFT_GROUND_CORAL = "leftGroundCoral"
    CENTER_GROUND_CORAL = "centerGroundCoral"
    RIGHT_GROUND_CORAL = "rightGroundCoral"

    LEFT_GROUND_ALGAE = "leftGroundAlgae"
    CENTER_GROUND_ALGAE = "centerGroundAlgae"
    RIGHT_GROUND_ALGAE = "rightGroundAlgae"

    REEF_ALGAE = "reefAlgae"
    PROCESSOR = "processor"
    NET = "net"

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
    timestamp: float = Field(10.0)
    position: AutoPathPoint = None
    success: bool = False

class AutoRaw (BaseModel):
    preload: Preload = "None"
    startPosition: AutoStartPosition
    leave: bool = False
    path: List[AutoPath]

# Teleop (including Endgame)

class BargeAction (str, Enum):
    UNSET = "unset"
    NONE = "None"
    PARK = "Park"
    DEEP = "Deep"
    SHALLOW = "Shallow"

class BargePosition (str, Enum):
    UNSET = "unset"
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"

class TeleopPathPoint (str, Enum):
    CORAL_STATION = "coralStation"

    GROUND_CORAL = "groundCoral"
    GROUND_ALGAE = "groundAlgae"

    REEF_ALGAE = "reefAlgae"
    PROCESSOR = "processor"
    NET = "net"

    L1_REEF = "l1Reef"
    L2_REEF = "l2Reef"
    L3_REEF = "l3Reef"
    L4_REEF = "l4Reef"

class TeleopPath (BaseModel):
    second: float
    position: TeleopPathPoint
    success: bool = False

class TeleopRaw (BaseModel):
    path: List[TeleopPath]
    hangTime: float
    bargeTried: BargeAction
    bargeResult: BargeAction
    bargePosition: BargePosition

# General Model

class ObjectiveMatchRawData (BaseModel):
    # "_id" field: Making sure that the data in temp and db has same id
    ulid: ULID
    scout: str
    matchLevel: MatchLevel
    matchNumber: int
    eventKey: str
    teamNumber: int
    alliance: Alliance
    auto : AutoRaw
    teleop: TeleopRaw

# Subjective Match Data (formerly known as Super Scout Data)

class SubjectiveRanking3 (IntEnum):
    FIRST = 1
    SECOND = 2
    THIRD = 3

class SubjectiveRanking2 (IntEnum):
    FIRST = 1
    SECOND = 2

class SubjectiveTeamRaw(BaseModel):
    team_number: int
    driver_awareness: SubjectiveRanking3
    coral_station_awareness: SubjectiveRanking2
    num_score_on_net: int
    mobility: SubjectiveRanking3
    defense: SubjectiveRanking3

class SubjectiveMatchRawData (BaseModel):
    ulid: ULID
    scout: str
    match_type: MatchLevel
    match_number: int
    event_key: str
    alliance: Alliance
    team1: SubjectiveTeamRaw
    team2: SubjectiveTeamRaw
    team3: SubjectiveTeamRaw

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

class PreloadCount(BaseModel):
    none: int
    coral: int
    algae: int

class StartPositionCount(BaseModel):
    left: int
    center: int
    right: int

class GamePieceActionAbsoluteResult (BaseModel):
    average: float
    stability: float

class GamePieceActionRelativeResult (BaseModel):
    rank: int
    zScore: float

class ReefCountAbsoluteResultBySide(BaseModel):
    l1: GamePieceActionAbsoluteResult
    l2: GamePieceActionAbsoluteResult
    l3: GamePieceActionAbsoluteResult
    l4: GamePieceActionAbsoluteResult

class ReefCountRelativeResultBySide(BaseModel):
    l1: GamePieceActionRelativeResult
    l2: GamePieceActionRelativeResult
    l3: GamePieceActionRelativeResult
    l4: GamePieceActionRelativeResult

class ReefResultBySide(BaseModel):
    AB: float
    CD: float
    EF: float
    GH: float
    IJ: float
    KL: float

class AutoAbsoluteResult(BaseModel):
    preloadCount: PreloadCount
    startPositionCount: StartPositionCount
    leaveSuccessRate: float
    reef: ReefCountAbsoluteResultBySide
    reefSuccessRateBySide: ReefResultBySide
    reefScoreBySide: ReefResultBySide
    reefScore: GamePieceActionAbsoluteResult
    processorScore: GamePieceActionAbsoluteResult
    netScore: GamePieceActionAbsoluteResult

class AutoRelativeResult(BaseModel):
    reef: ReefCountRelativeResultBySide
    reefScore: GamePieceActionRelativeResult
    processorScore: GamePieceActionRelativeResult
    netScore: GamePieceActionRelativeResult

class AbsoluteCycleTime(BaseModel):
    algae: GamePieceActionAbsoluteResult
    coral: GamePieceActionAbsoluteResult

class TeleopAbsoluteResult(BaseModel):
    reef: ReefCountAbsoluteResultBySide
    processorScore: GamePieceActionAbsoluteResult
    netScore: GamePieceActionAbsoluteResult
    cycleTime: AbsoluteCycleTime
    hang: GamePieceActionAbsoluteResult

class TeleopRelativeResult(BaseModel):
    reef: ReefCountRelativeResultBySide
    processorScore: GamePieceActionRelativeResult
    netScore: GamePieceActionRelativeResult
    cycleTime: AbsoluteCycleTime
    hang: GamePieceActionRelativeResult

class ObjectiveAbsoluteResult (BaseModel):
    teamNumber: int
    auto: AutoAbsoluteResult
    teleop: TeleopAbsoluteResult

class ObjectiveRelativeResult (BaseModel):
    teamNumber: int
    auto: AutoRelativeResult
    teleop: TeleopRelativeResult