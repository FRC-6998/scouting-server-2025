from enum import Enum
from operator import itemgetter

import numpy as np

from constants import RESULT_DATA_COLLECTION, OBJECTIVE_DATA_COLLECTION
from scripts.initdb import init_collection

raw_collection = init_collection(OBJECTIVE_DATA_COLLECTION)
result_collection = init_collection(RESULT_DATA_COLLECTION)

def get_abs_team_stats (data: list):
    return {
        "average": np.mean(data),
        "stability": np.std(data)
    }

def get_rel_team_stats (data: list, team_number: int, key: str):
    rank = 0
    data = sorted(data, key=itemgetter(key + ".average"), reverse=True)
    sorted_average = []

    for item in data:
        sorted_average.append(item[key + ".average"])
        if item["teamNumber"] == team_number:
            rank = data.index(item) + 1

    sorted_np = np.array(sorted_average)
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

# TIPS: Use asyncio.run() to run async function in sync function, to make sure it returns the real value you want.

async def get_auto_path (team_number: int):
    data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                "path": "$auto.path"
            }
        )
    ]

    return data

async def calc_auto_reef_level (team_number: int, level: ReefLevel):
    converted_level = convert_reef_level_to_pos(level)
    paths = await get_auto_path(team_number)

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


async def calc_auto_reef_score (team_number: int):
    all_reef_level = ["l1", "l2", "l3", "l4"]
    scores = []

    paths = await get_auto_path(team_number)
    for data in paths:
        reef_score = 0
        for level in all_reef_level:
            for pos in convert_reef_level_to_pos(level):
                reef_score += data.count({"path.position": pos})*get_reef_level_score_weight(level, "auto")
        scores.append(reef_score)

    return get_abs_team_stats(scores)

async def calc_auto_reef_level_relative (team_number: int, level: ReefLevel):

    average_data = [
        await result_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                level + ".average": "$auto.reef." + level + ".average"}
        )
    ]

    return get_rel_team_stats(average_data, team_number, level)

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
        case "tele":
            match level:
                case ReefLevel.L1:
                    return 2
                case ReefLevel.L2:
                    return 3
                case ReefLevel.L3:
                    return 4
                case ReefLevel.L4:
                    return 5

async def calc_auto_reef_score_by_side (team_number: int, side: ReefSide):
    converted_side = convert_reef_side_to_pos(side)
    side_paths = await get_auto_path(team_number)

    side_matched = []
    all_reef_level = ["l1", "l2", "l3", "l4"]
    for data in side_paths:
        score = 0
        for side in converted_side:
            for level in all_reef_level:
                score += (data.count({"path.position": convert_reef_level_side_to_pos(level, side)})
                            *get_reef_level_score_weight(level, "auto"))

        side_matched.append(score)

    return get_abs_team_stats(side_matched)

async def pack_auto_reef_data (team_number: int):
    data = {
        "level": {},
        "side": {}
    }
    for level in ReefLevel:
        data["level"][level] = await calc_auto_reef_level(team_number, level)

    for side in ReefSide:
        data["side"][side] = await calc_auto_reef_side(team_number, side)

    return data