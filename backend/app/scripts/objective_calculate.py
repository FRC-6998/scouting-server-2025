from enum import Enum
from operator import itemgetter
from typing import Dict

import numba
import numpy as np

from ..constants import OBJECTIVE_RAW_COLLECTION, OBJECTIVE_RESULT_COLLECTION
from ..model import TeleopPathPoint
from ..scripts.initdb import init_collection

raw_collection = init_collection(OBJECTIVE_RAW_COLLECTION)
result_collection = init_collection(OBJECTIVE_RESULT_COLLECTION)


@numba.jit(cache=True)
def get_abs_team_stats(data: list):
    data_array = np.array(data)
    return {
        "average": np.mean(data_array),
        "stability": np.std(data_array)
    }


async def get_rel_team_stats(team_number: int, key: str, period: str):
    unsorted_data = await result_collection.find(
        {},
        {
            "_id": 0,
            "team_number": 1,
            key + ".average": "$" + period + "." + key + ".average"
        }
    ).to_list(None)

    if not unsorted_data:  # Handle empty result case
        # Return default relative stats if no relevant data was found
        return {"relative_rank": None, "relative_percentile": None}

    data = sorted(unsorted_data, key=itemgetter(
        key + ".average"), reverse=True)

    return calc_relative(team_number, data, key)


@numba.jit(cache=True)
def calc_relative(team_number: int, data: list, key: str):
    rank = 0

    for item in data:
        data.append(item[key+".average"])
        if item["team_number"] == team_number:
            rank = data.index(item) + 1

    sorted_np = np.array(d[key] for d in data)
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


async def count_preload(team_number: int):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "preload": "$auto.preload"
        }
    ).to_list(None)
    none = raw_data.count({"preload": "none"})
    coral = raw_data.count({"preload": "coral"})
    algae = raw_data.count({"preload": "algae"})
    return {"none": none, "coral": coral, "algae": algae}


async def count_start_pos(team_number: int):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "start_position": "auto.start_position"
        }
    ).to_list(None)
    left = raw_data.count({"start_position": "left"})
    center = raw_data.count({"start_position": "center"})
    right = raw_data.count({"start_position": "right"})
    return {"left": left, "center": center, "right": right}


async def calc_leave_success_rate(team_number: int, is_percentage: int = 0):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {"_id": 0,
         "leave": "auto.leave"}
    ).to_list(None)
    count_try = len(raw_data)
    count_success = raw_data.count({"leave": True})
    match is_percentage:
        case 1:
            return count_success / count_try * 100
        case _:
            return count_success / count_try


def convert_reef_level_to_pos(level: str):
    match level:
        case ReefLevel.L1:
            return ["l1ReefAB", "l1ReefCD", "l1ReefEF", "l1ReefGH", "l1ReefIJ"]
        case ReefLevel.L2:
            return ["l2ReefAB", "l2ReefCD", "l2ReefEF", "l2ReefGH", "l2ReefIJ"]
        case ReefLevel.L3:
            return ["l3ReefAB", "l3ReefCD", "l3ReefEF", "l3ReefGH", "l3ReefIJ"]
        case ReefLevel.L4:
            return ["l4ReefAB", "l4ReefCD", "l4ReefEF", "l4ReefGH", "l4ReefIJ"]


def convert_reef_level_side_to_pos(level: str, side: str):
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


async def get_path(team_number: int, period: str = "auto"):
    data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "path": "$" + period + ".path"
        }
    ).to_list(None)

    return data


async def calc_reef_level(team_number: int, level: ReefLevel, period: str = "auto"):
    converted_level = convert_reef_level_to_pos(level)
    paths = await get_path(team_number, period)

    reef_matched = []
    for path in paths:
        if not isinstance(path, list):  # Ensure each path is a list
            continue

        count = 0
        for point in path:
            if isinstance(point, dict):  # Ensure each point is a dictionary
                if "position" in point and "success" in point:  # Validate keys
                    if point["position"] in converted_level and point["success"]:
                        count += 1
        reef_matched.append(count)

    # Handle edge case where reef_matched is empty
    if not reef_matched:
        reef_matched = [0]  # Assign a default value (e.g., no matches)

    abs_stats = get_abs_team_stats(reef_matched)
    rel_stats = await get_rel_team_stats(team_number, "reef." + str(level), period)

    merged_stats = {**abs_stats, **rel_stats}
    return merged_stats  # Use the merged dictionary


async def calc_reef_score(team_number: int, period: str = "auto"):
    all_reef_level = ["l1", "l2", "l3", "l4"]
    scores = []

    paths = await get_path(team_number, period)

    for data in paths:
        reef_score = 0
        for level in all_reef_level:
            for pos in convert_reef_level_to_pos(level):
                if isinstance(data, dict) and data.get("path.position") == pos:
                    reef_score += get_reef_level_score_weight(level, "auto")

                scores.append(reef_score)

    abs_team_stats = get_abs_team_stats(scores)
    rel_team_stats = await get_rel_team_stats(team_number, "reef_core", period)

    # Merging the dictionaries
    merged_stats = {**abs_team_stats, **rel_team_stats}

    return merged_stats


def convert_reef_side_to_pos(side: ReefSide):
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


def get_reef_level_score_weight(level: str, period: str):
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


async def calc_reef_score_by_side(team_number: int, side: ReefSide, period: str = "auto"):
    converted_side = convert_reef_side_to_pos(side)
    paths = await get_path(team_number, period)

    side_matched = []
    all_reef_level = ["l1", "l2", "l3", "l4"]
    for data in paths:
        score = 0
        for side in converted_side:
            for level in all_reef_level:
                if data.get("path.position") == convert_reef_level_side_to_pos(level, side):
                    score += get_reef_level_score_weight(level, "auto")

        side_matched.append(score)

    return get_abs_team_stats(side_matched)


async def calc_reef_success_rate_by_side(team_number: int, side: ReefSide, period: str = "auto"):
    converted_side = convert_reef_side_to_pos(side)
    paths = await get_path(team_number, period)

    matched = 0
    count_succeeded = 0

    if not isinstance(paths, list) or not all(isinstance(data, dict) for data in paths):
        raise ValueError(
            f"Expected 'paths' to be a list of dictionaries, got {type(paths)} with elements of type {type(paths[0]) if paths else 'unknown'}.")

    for path in paths:  # Iterate through each dictionary in 'paths'
        for pos in converted_side:
            if path.get("position") == pos:  # Match the position
                matched += 1
                if path.get("success"):  # Success if key exists and is truthy
                    count_succeeded += 1

    if matched == 0:  # Avoid division by zero
        return {side: 0.0}

    rate = count_succeeded / matched

    return {side: rate}


async def count_processor_score(team_number: int, period: str = "auto"):
    paths = await get_path(team_number, period)
    processor_score = []

    for data in paths:
        score = 0
        for path in data:
            if isinstance(path, Dict) and "success" in path:
                if path["success"]:
                    score += 6
        processor_score.append(score)

    abs_team_stats = get_abs_team_stats(processor_score)
    rel_team_stats = await get_rel_team_stats(team_number, "processor", period)
    # Use dictionary unpacking to merge them safely.
    return {**abs_team_stats, **rel_team_stats}


async def count_net_score(team_number: int, period: str = "auto"):
    paths = await get_path(team_number, period)
    net_score = []

    for data in paths:
        score = 0
        for path in data:
            # Default to False if no "success" key
            if isinstance(path, dict) and path.get("success", False):
                score += 4

        net_score.append(score)

    # Return computed stats
    abs_stats = get_abs_team_stats(net_score)
    rel_stats = await get_rel_team_stats(team_number, "net", period)
    return {**abs_stats, **rel_stats}


async def pack_auto_data(team_number: int):
    data = {
        "preload_count": await count_preload(team_number),
        "start_position_count": await count_start_pos(team_number),
        "leave_success_rate": await calc_leave_success_rate(team_number),
        "reef": {
            "l1": await calc_reef_level(team_number, ReefLevel.L1, "auto"),
            "l2": await calc_reef_level(team_number, ReefLevel.L2, "auto"),
            "l3": await calc_reef_level(team_number, ReefLevel.L3, "auto"),
            "l4": await calc_reef_level(team_number, ReefLevel.L4, "auto"),

        },
        "reef_success_rate_by_side": {
            "AB": await calc_reef_success_rate_by_side(team_number, ReefSide.AB, "auto"),
            "CD": await calc_reef_success_rate_by_side(team_number, ReefSide.CD, "auto"),
            "EF": await calc_reef_success_rate_by_side(team_number, ReefSide.EF, "auto"),
            "GH": await calc_reef_success_rate_by_side(team_number, ReefSide.GH, "auto"),
            "IJ": await calc_reef_success_rate_by_side(team_number, ReefSide.IJ, "auto"),
            "KL": await calc_reef_success_rate_by_side(team_number, ReefSide.KL, "auto")
        },
        "reef_score_by_side": {
            "AB": await calc_reef_score_by_side(team_number, ReefSide.AB, "auto"),
            "CD": await calc_reef_score_by_side(team_number, ReefSide.CD, "auto"),
            "EF": await calc_reef_score_by_side(team_number, ReefSide.EF, "auto"),
            "GH": await calc_reef_score_by_side(team_number, ReefSide.GH, "auto"),
            "IJ": await calc_reef_score_by_side(team_number, ReefSide.IJ, "auto"),
            "KL": await calc_reef_score_by_side(team_number, ReefSide.KL, "auto")
        },
        "reef_score": await calc_reef_score(team_number, "auto"),
        "processor_score": await count_processor_score(team_number, "auto"),
        "net_score": await count_net_score(team_number, "auto")
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

def search_cycle_time(data: list, cycle_type: str):
    start_pos = []
    end_pos = []

    start_point = []
    end_point = []

    if cycle_type == "coral":
        start_pos.extend([
            TeleopPathPoint.GROUND_CORAL,
            TeleopPathPoint.CORAL_STATION
        ])
        end_pos.extend([
            TeleopPathPoint.L1_REEF,
            TeleopPathPoint.L2_REEF,
            TeleopPathPoint.L3_REEF,
            TeleopPathPoint.L4_REEF
        ])
    elif cycle_type == "algae":
        start_pos.extend([
            TeleopPathPoint.REEF_ALGAE,
            TeleopPathPoint.GROUND_ALGAE
        ])
        end_pos.extend([
            TeleopPathPoint.NET,
            TeleopPathPoint.PROCESSOR
        ])

    # Filter the data for start and end points
    start_points = []
    end_points = []

    for path in data:
        if path.get("position") in start_pos and path.get("success"):
            start_points.append(path)
        elif path.get("position") in end_pos:
            end_points.append(path)

    cycle_time = []
    for start, end in zip(start_point, end_point):
        cycle_time.append(end["time"] - start["time"])

    return cycle_time


async def calc_cycle_time(team_number: int, cycle_type: str):
    data = await get_path(team_number, "teleop")
    cycle_times = search_cycle_time(data, cycle_type)

    if not cycle_times:
        # Handle empty cycle_times by returning default values
        return {"abs_stats": {}, "rel_stats": {}}  # Replace with meaningful defaults if needed


    return get_abs_team_stats(cycle_times) | await get_rel_team_stats(team_number, "cycle_time", "teleop")


async def count_hang(team_number):
    data = await get_path(team_number, "teleop")
    hang_time = [item.get("hangTime", 0) for item in data if "hangTime" in item]
    # Handle empty hang_time case
    if not hang_time:  # If hang_time is an empty list
        # Substitute default values for absolute and relative stats
        abs_stats = {"total_hang_time": 0}  # Define meaningful default stats
        rel_stats = {"relative_hang_score": 0}  # Define meaningful placeholder for relative stats
    else:
        # Calculate absolute and relative stats using available hang_time
        abs_stats = get_abs_team_stats(hang_time)
        rel_stats = await get_rel_team_stats(team_number, "hang_time", "teleop")

    return abs_stats | rel_stats


async def pack_teleop_data(team_number: int):
    data = {
        "reef": {
            "l1": await calc_reef_level(team_number, ReefLevel.L1, "teleop"),
            "l2": await calc_reef_level(team_number, ReefLevel.L2, "teleop"),
            "l3": await calc_reef_level(team_number, ReefLevel.L3, "teleop"),
            "l4": await calc_reef_level(team_number, ReefLevel.L4, "teleop"),

        },
        "processor_score": await count_processor_score(team_number, "teleop"),
        "net_score": await count_net_score(team_number, "teleop"),
        "cycle_time": {
            "coral": await calc_cycle_time(team_number, "coral"),
            "algae": await calc_cycle_time(team_number, "algae")
        },
        "hang": await count_hang(team_number)
    }

    return data


async def get_comments(team_number: int):
    # Get all documents matching the query and project only the 'comments' field
    cursor = raw_collection.find(
        {"team_number": team_number},
        {"_id": 0, "comments": 1}  # Fixed projection syntax
    )
    # Convert the cursor to a list of documents
    documents = await cursor.to_list(length=None)

    # Extract the comments from each document, if they exist
    comments = [doc.get("comments") for doc in documents if "comments" in doc]

    return comments  # Return the list of comments

async def pack_obj_data(team_number: int):
    data = {
        "team_number": team_number,
        "auto": await pack_auto_data(team_number),
        "teleop": await pack_teleop_data(team_number),
        "comments": await get_comments(team_number)
    }

    return data


async def post_obj_results(team_number: int):
    data = await pack_obj_data(team_number)
    filter_query = {"team_number": team_number}
    replacement = data
    await result_collection.replace_one(filter_query, replacement, bypass_document_validation=False, session=None, upsert=True)
