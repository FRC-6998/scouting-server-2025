import statistics
from operator import itemgetter
from typing import Any

import numpy as np
from scipy import stats

from constants import RESULT_DATA_COLLECTION, OBJECTIVE_DATA_COLLECTION
from scripts.initdb import init_collection

raw_collection = init_collection(OBJECTIVE_DATA_COLLECTION)
result_collection = init_collection(RESULT_DATA_COLLECTION)

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

async def calc_auto_reef (team_number: int, level: str):
    raw_data = [
        await raw_collection.find(
            {"teamNumber": team_number},
            {
                "_id": 0,
                "path": "$auto.path"
            }
        )
    ]
    reef_count = []
    for data in raw_data:
        reef_count.append(data.count({"auto.auto_path.position": level}))
    average = np.mean(reef_count)
    standard_derivation = np.std(reef_count)
    """
    Unipards use "stability" as a measurement of the performance of the robot
    - stability is the reciprocal of coefficient of variation (CV)
    - CV := standard_derivation / average
    - stability := average / standard_derivation
    - More stable performance will have higher stability value 
    """
    stability = average / standard_derivation
    return {'average': average, 'stability': stability}

async def calc_reef_relative(team_number: int, level: str):
    rank = -1
    z_score = 0.0
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