from collections import Counter

import numpy

from scripts.initdb import init_collection

collection = init_collection("objective")

async def count_preload (team_number: int):
    raw_data = [await collection.find({"team_number": team_number}, {"_id": 0, "preload": 1})]
    none = raw_data.count({"preload": "None"})
    coral = raw_data.count({"preload": "Coral"})
    algae = raw_data.count({"preload": "Algae"})
    return {"none": none, "coral": coral, "algae": algae}

async def count_start_pos (team_number: int):
    raw_data = [await collection.find({"team_number": team_number}, {"_id": 0, "start_position": 1})]
    side = raw_data.count({"start_position": "Side"})
    center = raw_data.count({"start_position": "Center"})
    middle = raw_data.count({"start_position": "Middle"})
    return {"side": side, "center": center, "middle": middle}

async def calc_leave_success_rate (team_number:int, is_percentage : int = 0):
    raw_data = [await collection.find({"team_number": team_number}, {"_id": 0, "leave": 1})]
    count_try = len(raw_data)
    count_success = raw_data.count({"leave": True})
    match is_percentage:
        case 1:
            return count_success / count_try * 100
        case _:
            return count_success

async def calc_auto_reef (team_number: int, level: str):
    raw_data = [await collection.find({"team_number": team_number}, {"_id": 0, "auto.auto_path": 1})]
    reef_count = []
    for data in raw_data:
        reef_count.append(data.count({"auto.auto_path.position": level}))
    average = numpy.mean(reef_count)
    standard_derivation = numpy.std(reef_count)
    """
    Unipards use "stability" to measure the consistency of the team's performance in the auto phase.
    - stability is the reciprocal of coefficient of variation (CV)
    - CV = standard_derivation / average
    - stability = average / standard_derivation
    - More stable performance will have higher stability value 
    """
    stability = average / standard_derivation
    return {'average': average, 'stability': stability}

# TODO: Add reef's z-score and ranking functions