import asyncio
from enum import Enum
from operator import itemgetter

import numpy as np

from constants import RESULT_DATA_COLLECTION, OBJECTIVE_DATA_COLLECTION
from scripts.initdb import init_collection

raw_collection = init_collection(OBJECTIVE_DATA_COLLECTION)
result_collection = init_collection(RESULT_DATA_COLLECTION)

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
            return count_success

def convert_reef_level (level: ReefLevel):
    match level:
        case ReefLevel.L1:
            return ["l1ReefAB", "l1ReefCD", "l1ReefEF", "l1ReefGH", "l1ReefIJ", "l1ReefKL"]
        case ReefLevel.L2:
            return ["l2ReefAB", "l2ReefCD", "l2ReefEF", "l2ReefGH", "l2ReefIJ", "l2ReefKL"]
        case ReefLevel.L3:
            return ["l3ReefAB", "l3ReefCD", "l3ReefEF", "l3ReefGH", "l3ReefIJ", "l3ReefKL"]
        case ReefLevel.L4:
            return ["l4ReefAB", "l4ReefCD", "l4ReefEF", "l4ReefGH", "l4ReefIJ", "l4ReefKL"]

# TIPS: Use asyncio.run() to run async function in sync function, to make sure it returns the real value you want.

async def async_get_auto_path (team_number: int):
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

def get_auto_path (team_number: int):
    return asyncio.get_event_loop().run_until_complete(async_get_auto_path(team_number))

async def calc_auto_reef (team_number: int, level: ReefLevel):
    converted_level = convert_reef_level(level)
    paths = get_auto_path(team_number)

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

async def calc_reef_relative (team_number: int, level: ReefLevel):
    rank = -1
    sorted_average = []

    average_data = [
        await result_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                level + ".average": "$auto.reef." + level + ".average"}
        )
    ]

    sorted_data = sorted(average_data, key= itemgetter(level + ".average"), reverse=True)

    for item in sorted_data:
        sorted_average.append(item[level + ".average"])
        if item["teamNumber"] == team_number:
            rank = sorted_data.index(item) + 1

    sorted_np = np.array(sorted_average)
    z_score = (sorted_np[rank-1] - np.average(sorted_np)) / np.std(sorted_np)

    return {"rank": rank, "zScore": z_score}

def convert_reef_side (side: ReefSide):
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

async def calc_reef_side (team_number: int, side: ReefSide):
    converted_side = convert_reef_side(side)
    side_paths = get_auto_path(team_number)

    side_matched = []
    for data in side_paths:
        for pos in converted_side:
            side_matched.append(data.count({"path.position": pos}))

    average = np.mean(side_matched)
    standard_derivation = np.std(side_matched)
    stability = average / standard_derivation

    return {"average": average, "stability": stability}