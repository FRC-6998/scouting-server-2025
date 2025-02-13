from enum import Enum
from operator import itemgetter

import numba
import numpy as np

from constants import RESULT_DATA_COLLECTION, OBJECTIVE_DATA_COLLECTION
from model import TeleopPathPoint
from scripts.initdb import init_collection

raw_collection = init_collection(OBJECTIVE_DATA_COLLECTION)
result_collection = init_collection(RESULT_DATA_COLLECTION)

@numba.jit(cache=True)
def get_abs_team_stats (data: list):
    return {
        "average": np.mean(data),
        "stability": np.std(data)
    }

async def get_rel_team_stats (team_number: int, key: str, period: str):
    unsorted_data = [
        await result_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                key + ".average": "$" + period + "." + key + ".average"
            }
        )
    ]
    data = sorted(unsorted_data, key=itemgetter(key + ".average"), reverse=True)

    return calc_relative(team_number, data, key)

@numba.jit(cache=True)
def calc_relative (team_number: int, data: list, key: str):
    rank = 0

    for item in data:
        data.append(item[key+".average"])
        if item["teamNumber"] == team_number:
            rank = data.index(item) + 1

    sorted_np = np.array(data)
    z_score = (sorted_np[rank - 1] - np.average(sorted_np)) / np.std(sorted_np)

    return {"rank": rank, "z_score": z_score}

class ReefLevel(str, Enum):
    L1 = "l1"
    L2 = "l2"
    L3 = "l3"
    L4 = "l4"

class ReefSide(str, Enum):
    AB = "AB"
    CD = "CD"
    EF = "EF"
    GH = "GH"
    IJ = "IJ"
    KL = "KL"

async def count_preload (team_number: int):
    raw_data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                "preload": "$auto.preload"
            }
        )
    ]
    none = raw_data.count({"preload": "None"})
    coral = raw_data.count({"preload": "Coral"})
    algae = raw_data.count({"preload": "Algae"})
    return {"none": none, "coral": coral, "algae": algae}

async def count_start_pos (team_number: int):
    raw_data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                "startPosition": "auto.startPosition"
            }
        )
    ]
    left = raw_data.count({"start_position": "left"})
    center = raw_data.count({"start_position": "center"})
    right = raw_data.count({"start_position": "right"})
    return {"left": left, "center": center, "right": right}

async def calc_leave_success_rate (team_number:int, is_percentage : int = 0):
    raw_data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {"_id": 0,
             "leave": "auto.leave"}
        )
    ]
    count_try = len(raw_data)
    count_success = raw_data.count({"leave": True})
    match is_percentage:
        case 1:
            return count_success / count_try * 100
        case _:
            return count_success / count_try

def convert_reef_level_to_pos (level: str):
    match level:
        case ReefLevel.L1:
            return ["l1ReefAB", "l1ReefCD", "l1ReefEF", "l1ReefGH", "l1ReefIJ"]
        case ReefLevel.L2:
            return ["l2ReefAB", "l2ReefCD", "l2ReefEF", "l2ReefGH", "l2ReefIJ"]
        case ReefLevel.L3:
            return ["l3ReefAB", "l3ReefCD", "l3ReefEF", "l3ReefGH", "l3ReefIJ"]
        case ReefLevel.L4:
            return ["l4ReefAB", "l4ReefCD", "l4ReefEF", "l4ReefGH", "l4ReefIJ"]


def convert_reef_level_side_to_pos (level: str, side: str):
    match level:
        case ReefLevel.L1:
            match side:
                case ReefSide.AB:
                    return "l1ReefAB"
                case ReefSide.CD:
                    return "l1ReefCD"
                case ReefSide.EF:
                    return "l1ReefEF"
                case ReefSide.GH:
                    return "l1ReefGH"
                case ReefSide.IJ:
                    return "l1ReefIJ"
                case ReefSide.KL:
                    return "l1ReefKL"
        case ReefLevel.L2:
            match side:
                case ReefSide.AB:
                    return "l2ReefAB"
                case ReefSide.CD:
                    return "l2ReefCD"
                case ReefSide.EF:
                    return "l2ReefEF"
                case ReefSide.GH:
                    return "l2ReefGH"
                case ReefSide.IJ:
                    return "l2ReefIJ"
                case ReefSide.KL:
                    return "l2ReefKL"
        case ReefLevel.L3:
            match side:
                case ReefSide.AB:
                    return "l3ReefAB"
                case ReefSide.CD:
                    return "l3ReefCD"
                case ReefSide.EF:
                    return "l3ReefEF"
                case ReefSide.GH:
                    return "l3ReefGH"
                case ReefSide.IJ:
                    return "l3ReefIJ"
                case ReefSide.KL:
                    return "l3ReefKL"
        case ReefLevel.L4:
            match side:
                case ReefSide.AB:
                    return "l4ReefAB"
                case ReefSide.CD:
                    return "l4ReefCD"
                case ReefSide.EF:
                    return "l4ReefEF"
                case ReefSide.GH:
                    return "l4ReefGH"
                case ReefSide.IJ:
                    return "l4ReefIJ"
                case ReefSide.KL:
                    return "l4ReefKL"

async def get_path (team_number: int, period: str = "auto"):
    data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                "path": "$" + period + ".path"
            }
        )
    ]

    return data

async def calc_reef_level (team_number: int, level: ReefLevel, period: str = "auto"):
    converted_level = convert_reef_level_to_pos(level)
    paths = await get_path(team_number, period)

    reef_matched = []
    for data in paths:
        for pos in converted_level:
            reef_matched.append(data.count({"path.position": pos}))

    average = np.mean(reef_matched)
    standard_derivation = np.std(reef_matched)
    """
    Unipards use "stability" as a measurement of the performance of the robot
    - stability is the reciprocal of coefficient of variation (CV)
    - CV := standard_derivation / average
    - stability := average / standard_derivation
    - More stable performance will have higher stability value 
    """
    stability = average / standard_derivation
    return {'average': average, 'stability': stability}


async def calc_reef_score (team_number: int, period: str = "auto"):
    all_reef_level = ["l1", "l2", "l3", "l4"]
    scores = []

    paths = await get_path(team_number, period)

    for data in paths:
        reef_score = 0
        for level in all_reef_level:
            for pos in convert_reef_level_to_pos(level):
                reef_score += data.count({"path.position": pos})*get_reef_level_score_weight(level, "auto")
        scores.append(reef_score)

    return get_abs_team_stats(scores)

async def calc_reef_score_relative (team_number: int, period: str = "auto"):
    return await get_rel_team_stats(team_number, "reefScore", period)

async def calc_reef_level_relative (team_number: int, level: ReefLevel):
    return await get_rel_team_stats(team_number, "reef." + level, "auto")

def convert_reef_side_to_pos (side: ReefSide):
    match side:
        case ReefSide.AB:
            return ["l1ReefAB", "l2ReefAB", "l3ReefAB", "l4ReefAB"]
        case ReefSide.CD:
            return ["l1ReefCD", "l2ReefCD", "l3ReefCD", "l4ReefCD"]
        case ReefSide.EF:
            return ["l1ReefEF", "l2ReefEF", "l3ReefEF", "l4ReefEF"]
        case ReefSide.GH:
            return ["l1ReefGH", "l2ReefGH", "l3ReefGH", "l4ReefGH"]
        case ReefSide.IJ:
            return ["l1ReefIJ", "l2ReefIJ", "l3ReefIJ", "l4ReefIJ"]
        case ReefSide.KL:
            return ["l1ReefKL", "l2ReefKL", "l3ReefKL", "l4ReefKL"]


def get_reef_level_score_weight (level: str, period: str):
    match period:
        case "auto":
            match level:
                case ReefLevel.L1:
                    return 3
                case ReefLevel.L2:
                    return 4
                case ReefLevel.L3:
                    return 6
                case ReefLevel.L4:
                    return 7
        case "teleop":
            match level:
                case ReefLevel.L1:
                    return 2
                case ReefLevel.L2:
                    return 3
                case ReefLevel.L3:
                    return 4
                case ReefLevel.L4:
                    return 5

async def calc_reef_score_by_side (team_number: int, side: ReefSide, period: str = "auto"):
    converted_side = convert_reef_side_to_pos(side)
    paths = await get_path(team_number, period)

    side_matched = []
    all_reef_level = ["l1", "l2", "l3", "l4"]
    for data in paths:
        score = 0
        for side in converted_side:
            for level in all_reef_level:
                score += (data.count({"path.position": convert_reef_level_side_to_pos(level, side)})
                            *get_reef_level_score_weight(level, "auto"))

        side_matched.append(score)

    return get_abs_team_stats(side_matched)

async def calc_reef_success_rate_by_side (team_number: int, side: ReefSide, period: str = "auto"):
    converted_side = convert_reef_side_to_pos(side)
    paths = await get_path(team_number, period)

    matched = 0
    count_succeeded = 0
    for data in paths:
        for pos in converted_side:
            for path in data:
                if path["position"] == pos:
                    matched += 1
                    if path["success"]:
                        count_succeeded += 1

    rate = count_succeeded / matched

    return {side: rate}

async def count_processor_score (team_number: int, period: str = "auto"):
    paths = await get_path(team_number, period)
    processor_score = []

    for data in paths:
        score = 0
        for path in data:
            if path["success"]:
                score += 6
        processor_score.append(score)

    return get_abs_team_stats(processor_score)

async def count_processor_score_relative (team_number: int, period: str = "auto"):
    return await get_rel_team_stats(team_number, "processor", period)

async def count_net_score (team_number: int, period: str = "auto"):
    paths = await get_path(team_number, period)
    net_score = []

    for data in paths:
        score = 0
        for path in data:
            if path["success"]:
                score += 4
        net_score.append(score)
    return get_abs_team_stats(net_score)

async def count_net_score_relative (team_number: int, period: str = "auto"):
    return await get_rel_team_stats(team_number, "net", period)

async def pack_auto_abs_data (team_number: int):
    data = {
        "preloadCount": await count_preload(team_number),
        "startPositionCount": await count_start_pos(team_number),
        "leaveSuccessRate": await calc_leave_success_rate(team_number),
        "reef": {
            "l1": await calc_reef_level(team_number, ReefLevel.L1, "auto"),
            "l2": await calc_reef_level(team_number, ReefLevel.L2, "auto"),
            "l3": await calc_reef_level(team_number, ReefLevel.L3, "auto"),
            "l4": await calc_reef_level(team_number, ReefLevel.L4, "auto"),

        },
        "reefSuccessRateBySide":{
            "AB": await calc_reef_success_rate_by_side(team_number, ReefSide.AB, "auto"),
            "CD": await calc_reef_success_rate_by_side(team_number, ReefSide.CD, "auto"),
            "EF": await calc_reef_success_rate_by_side(team_number, ReefSide.EF, "auto"),
            "GH": await calc_reef_success_rate_by_side(team_number, ReefSide.GH, "auto"),
            "IJ": await calc_reef_success_rate_by_side(team_number, ReefSide.IJ, "auto"),
            "KL": await calc_reef_success_rate_by_side(team_number, ReefSide.KL, "auto")
        },
        "reefScoreBySide": {
            "AB": await calc_reef_score_by_side(team_number, ReefSide.AB, "auto"),
            "CD": await calc_reef_score_by_side(team_number, ReefSide.CD, "auto"),
            "EF": await calc_reef_score_by_side(team_number, ReefSide.EF, "auto"),
            "GH": await calc_reef_score_by_side(team_number, ReefSide.GH, "auto"),
            "IJ": await calc_reef_score_by_side(team_number, ReefSide.IJ, "auto"),
            "KL": await calc_reef_score_by_side(team_number, ReefSide.KL, "auto")
        },
        "reefScore": await calc_reef_score(team_number, "auto"),
        "processorScore": await count_processor_score(team_number, "auto"),
        "netScore": await count_net_score(team_number, "auto")
    }

    return data

async def pack_auto_rel_data (team_number: int):
    data = {
        "preloadCount": await count_preload(team_number),
        "startPositionCount": await count_start_pos(team_number),
        "leaveSuccessRate": await calc_leave_success_rate(team_number),
        "reef": {
            "l1": await calc_reef_level_relative(team_number, ReefLevel.L1),
            "l2": await calc_reef_level_relative(team_number, ReefLevel.L2),
            "l3": await calc_reef_level_relative(team_number, ReefLevel.L3),
            "l4": await calc_reef_level_relative(team_number, ReefLevel.L4),

        },
        "reefScore": await calc_reef_score_relative(team_number, "auto"),
        "processorScore": await count_processor_score_relative(team_number, "auto"),
        "netScore": await count_net_score_relative(team_number, "auto")
    }

    return data

"""
[Type of cycles]
A. CORAL Cycle
    - GROUND -> REEF
    - CORAL STATION -> REEF
B. ALGAE Cycle
    - REEF -> NET
    - GROUND -> NET
    - REEF -> PROCESSOR
    - GROUND -> PROCESSOR

"""

@numba.jit(cache=True)
def search_cycle_time(data: list, cycle_type: str):
    start_pos = []
    end_pos = []

    start_point =[]
    end_point = []

    match cycle_type:
        case "algae":
            start_pos.append([
                TeleopPathPoint.GROUND_CORAL,
                TeleopPathPoint.CORAL_STATION
            ])
            end_pos.append([
                TeleopPathPoint.L1_REEF,
                TeleopPathPoint.L2_REEF,
                TeleopPathPoint.L3_REEF,
                TeleopPathPoint.L4_REEF
            ])

        case "algae":
            start_pos.append([
                TeleopPathPoint.REEF_ALGAE,
                TeleopPathPoint.GROUND_ALGAE
            ])
            end_pos.append([
                TeleopPathPoint.NET,
                TeleopPathPoint.PROCESSOR
            ])

    for path in data:
        if path["position"] in start_pos and path["success"] == True:
            start_point.append(path)
        elif path["position"] in end_pos:
            end_point.append(path)
            break

    cycle_time = []
    for start, end in zip(start_point, end_point):
        cycle_time.append(end["time"] - start["time"])

    return cycle_time

async def calc_cycle_time_abs(team_number: int, cycle_type: str):
    data = await get_path(team_number, "teleop")
    cycle_times = search_cycle_time(data, cycle_type)

    return get_abs_team_stats(cycle_times)


async def count_hang_abs(team_number):
    data = await get_path(team_number, "teleop")
    hang_time = [item["hangTime"] for item in data]
    return get_abs_team_stats(hang_time) | await get_rel_team_stats(team_number, "hangTime", "teleop")

async def count_hang_rel(team_number):
    return await get_rel_team_stats(team_number, "hang", "teleop")

async def pack_teleop_abs_data (team_number: int):
    data = {
        "reef": {
            "l1": await calc_reef_level(team_number, ReefLevel.L1, "teleop"),
            "l2": await calc_reef_level(team_number, ReefLevel.L2, "teleop"),
            "l3": await calc_reef_level(team_number, ReefLevel.L3, "teleop"),
            "l4": await calc_reef_level(team_number, ReefLevel.L4, "teleop"),

        },
        "processorScore": await count_processor_score(team_number, "teleop"),
        "netScore": await count_net_score(team_number, "teleop"),
        "cycleTime": {
            "coral": await calc_cycle_time_abs(team_number, "coral"),
            "algae": await calc_cycle_time_abs(team_number, "algae")
        },
        "hang": await count_hang_abs(team_number)
    }

    return data

async def pack_teleop_rel_data (team_number: int):
    data = {
        "reef": {
            "l1": await calc_reef_level_relative(team_number, ReefLevel.L1),
            "l2": await calc_reef_level_relative(team_number, ReefLevel.L2),
            "l3": await calc_reef_level_relative(team_number, ReefLevel.L3),
            "l4": await calc_reef_level_relative(team_number, ReefLevel.L4),

        },
        "processorScore": await count_processor_score_relative(team_number, "teleop"),
        "netScore": await count_net_score_relative(team_number, "teleop"),
        "cycleTime": {
            "coral": await calc_cycle_time_abs(team_number, "coral"),
            "algae": await calc_cycle_time_abs(team_number, "algae")
        },
        "hang": await count_hang_rel(team_number)
    }

    return data

async def pack_obj_abs_data (team_number: int):
    data = {
        "teamNumber": team_number,
        "auto": await pack_auto_abs_data(team_number),
        "teleop": await pack_teleop_abs_data(team_number),
    }

    return data

async def pack_obj_rel_data (team_number: int):
    data = {
        "teamNumber": team_number,
        "auto": await pack_auto_rel_data(team_number),
        "teleop": await pack_teleop_rel_data(team_number)
    }