from enum import Enum
from operator import itemgetter

import numba
import numpy as np

from .util import init_collection, get_all_teams
from ..constants import OBJECTIVE_RAW_COLLECTION, OBJECTIVE_RESULT_COLLECTION, ALL_REEF_LEVELS
from ..model import TeleopPathPoint

raw_collection = init_collection(OBJECTIVE_RAW_COLLECTION)
result_collection = init_collection(OBJECTIVE_RESULT_COLLECTION)


@numba.jit(cache=True)
def get_abs_team_stats(data: list):
    data_array = np.array(data)

    return {
        "average": np.mean(data_array),
        "stability": np.std(data_array)
    }


async def get_rel_team_stats(team_number: str, key: str, period: str):
    # Query to find documents in result_collection
    print (f"${period}.{key}.average")
    unsorted_data = await result_collection.find(
        {},  # Query criteria
        {
            "_id": 0,
            "team_number": 1,
            key: f"${period}.{key}.average"
        }
    ).to_list(None)
    print ({"unsorted_data": unsorted_data})

    if not unsorted_data:  # Handle case where no data is returned by the query
        # Default relative statistics when no data is found
        return {"rank": None, "z_score": None}


    # Sort only the valid data by the key
    data = sorted(unsorted_data, key=itemgetter(key), reverse=True)

    print (data)

    # Calculate the relative stats for the current team
    return calc_relative(team_number, data, key)


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


async def count_preload(team_number: str):
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
    print({"count_preload":{"none": none, "coral": coral, "algae": algae}})
    return {"none": none, "coral": coral, "algae": algae}


async def count_start_pos(team_number: str):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "start_position": "$auto.start_position"
        }
    ).to_list(None)
    left = raw_data.count({"start_position": "left"})
    center = raw_data.count({"start_position": "center"})
    right = raw_data.count({"start_position": "right"})
    print({"count_start_pos": {"left": left, "center": center, "right": right}})
    return {"left": left, "center": center, "right": right}


async def calc_leave_success_rate(team_number: str, is_percentage: int = 0):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {"_id": 0,
         "leave": "$auto.leave"}
    ).to_list(None)
    count_try = len(raw_data)
    count_success = raw_data.count({"leave": True})

    if count_try == 0:
        return 0

    print({"calc_leave_success_rate": count_success / count_try})

    match is_percentage:
        case 1:
            return count_success / count_try * 100
        case _:
            return count_success / count_try


def convert_reef_level_to_pos(level: str):
    match level:
        case ReefLevel.L1.value:
            return ["l1ReefAB", "l1ReefCD", "l1ReefEF", "l1ReefGH", "l1ReefIJ"]
        case ReefLevel.L2.value:
            return ["l2ReefAB", "l2ReefCD", "l2ReefEF", "l2ReefGH", "l2ReefIJ"]
        case ReefLevel.L3.value:
            return ["l3ReefAB", "l3ReefCD", "l3ReefEF", "l3ReefGH", "l3ReefIJ"]
        case ReefLevel.L4.value:
            return ["l4ReefAB", "l4ReefCD", "l4ReefEF", "l4ReefGH", "l4ReefIJ"]


def convert_reef_level_side_to_pos(level: str, side: str):
    match level:
        case ReefLevel.L1.value:
            match side:
                case ReefSide.AB.value:
                    return "l1ReefAB"
                case ReefSide.CD.value:
                    return "l1ReefCD"
                case ReefSide.EF.value:
                    return "l1ReefEF"
                case ReefSide.GH.value:
                    return "l1ReefGH"
                case ReefSide.IJ.value:
                    return "l1ReefIJ"
                case ReefSide.KL.value:
                    return "l1ReefKL"
        case ReefLevel.L2.value:
            match side:
                case ReefSide.AB.value:
                    return "l2ReefAB"
                case ReefSide.CD.value:
                    return "l2ReefCD"
                case ReefSide.EF.value:
                    return "l2ReefEF"
                case ReefSide.GH.value:
                    return "l2ReefGH"
                case ReefSide.IJ.value:
                    return "l2ReefIJ"
                case ReefSide.KL.value:
                    return "l2ReefKL"
        case ReefLevel.L3.value:
            match side:
                case ReefSide.AB.value:
                    return "l3ReefAB"
                case ReefSide.CD.value:
                    return "l3ReefCD"
                case ReefSide.EF.value:
                    return "l3ReefEF"
                case ReefSide.GH.value:
                    return "l3ReefGH"
                case ReefSide.IJ.value:
                    return "l3ReefIJ"
                case ReefSide.KL.value:
                    return "l3ReefKL"
        case ReefLevel.L4.value:
            match side:
                case ReefSide.AB.value:
                    return "l4ReefAB"
                case ReefSide.CD.value:
                    return "l4ReefCD"
                case ReefSide.EF.value:
                    return "l4ReefEF"
                case ReefSide.GH.value:
                    return "l4ReefGH"
                case ReefSide.IJ.value:
                    return "l4ReefIJ"
                case ReefSide.KL.value:
                    return "l4ReefKL"


async def get_path(team_number: str, period: str = "auto"):
    data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "path": "$" + period + ".path"
        }
    ).to_list(None)

    print({"get_path": data})
    return data

async def calc_auto_reef_level_abs(team_number: str, level: str):
    converted_level = convert_reef_level_to_pos(level)
    # print (converted_level)
    matches = await get_path(team_number, "auto")

    reef_matched = []
    for paths in matches:
        matched = 0
        for single_path in paths["path"]:
            if single_path.get("point") in converted_level:
                matched += 1
                # print ("got it")
        reef_matched.append(matched)

    # print (reef_matched)

    # Handle edge case where reef_matched is empty
    if not reef_matched:
        reef_matched = [0]  # Assign a default value (e.g., no matches)

    return get_abs_team_stats(reef_matched)

def convert_teleop_reef_level_to_pos(level: str):

    match level:
        case ReefLevel.L1.value:
            return "l1Reef"
        case ReefLevel.L2.value:
            return "l2Reef"
        case ReefLevel.L3.value:
            return "l3Reef"
        case ReefLevel.L4.value:
            return "l4Reef"


async def calc_teleop_reef_level_abs(team_number: str, level: str):
    converted_level = convert_teleop_reef_level_to_pos(level)
    # print (converted_level)
    matches = await get_path(team_number, "teleop")

    print({"teleop_test": converted_level})

    reef_matched = []
    for paths in matches:
        matched = 0
        for single_path in paths["path"]:
            if single_path.get("point") == converted_level:
                matched += 1
                # print ("got it")
        reef_matched.append(matched)

    return get_abs_team_stats(reef_matched)



def calc_relative(team_number: str, data: list, key: str):
    print ({"initialize_relative": data})

    rank = 0

    # Extract the values from data for key into a list
    for item in data:
        if item.get("team_number") == team_number:
            rank = data.index(item) + 1
        # Rank matches the 1-based index in sorted order
    # Convert the list of values into a NumPy array
    sorted_np = np.array([item.get(key) for item in data])

    if rank == 0 or np.std(sorted_np) == 0:
        return {"rank": rank, "z_score": 0.0}

    # Calculate the z-score for the team's rank
    z_score = float((sorted_np[rank - 1] - np.average(sorted_np)) / np.std(sorted_np))

    if np.isnan(z_score):
        z_score = 0.0

    return {"rank": rank, "z_score": z_score}


async def calc_reef_level_rel(team_number: str, level: str, period: str):
    unsorted_data = await result_collection.find(
        {},  # Query criteria
        {
            "_id": 0,
            "team_number": 1,
            level: f"${period}.reef.{level}.average"
        }
    ).to_list(None)

    print ({"test_reef_level_rel":unsorted_data})

    data = sorted(unsorted_data, key=itemgetter(level), reverse=True)

    # print ({"calc_reef_level_rel": calc_reef_side_relative(team_number, data, level)})

    return calc_relative(team_number, data, level)

async def calc_auto_reef_score_abs(team_number: str):
    scores = []

    # Get paths for the given team and period
    matches = await get_path(team_number, "auto")

    for paths in matches:
        score = 0
        for single_path in paths["path"]:
            for level in ALL_REEF_LEVELS:
                d_score = get_reef_level_score_weight(level, "auto")
                for pos in convert_reef_level_to_pos(level):
                    if single_path.get("point") == pos:
                        score += d_score
                        break
        scores.append(score)

    # print (scores)
    return get_abs_team_stats(scores)

async def calc_auto_reef_score_rel(team_number: str):
    return await get_rel_team_stats(team_number, "reef_score", "auto")


def convert_auto_reef_side_to_pos(side: str):
    match side:
        case ReefSide.AB.value:
            return ["l1ReefAB", "l2ReefAB", "l3ReefAB", "l4ReefAB"]
        case ReefSide.CD.value:
            return ["l1ReefCD", "l2ReefCD", "l3ReefCD", "l4ReefCD"]
        case ReefSide.EF.value:
            return ["l1ReefEF", "l2ReefEF", "l3ReefEF", "l4ReefEF"]
        case ReefSide.GH.value:
            return ["l1ReefGH", "l2ReefGH", "l3ReefGH", "l4ReefGH"]
        case ReefSide.IJ.value:
            return ["l1ReefIJ", "l2ReefIJ", "l3ReefIJ", "l4ReefIJ"]
        case ReefSide.KL.value:
            return ["l1ReefKL", "l2ReefKL", "l3ReefKL", "l4ReefKL"]


def get_reef_level_score_weight(level: str, period: str):
    match period:
        case "auto":
            match level:
                case ReefLevel.L1.value:
                    return 3
                case ReefLevel.L2.value:
                    return 4
                case ReefLevel.L3.value:
                    return 6
                case ReefLevel.L4.value:
                    return 7
        case "teleop":
            match level:
                case ReefLevel.L1.value:
                    return 2
                case ReefLevel.L2.value:
                    return 3
                case ReefLevel.L3.value:
                    return 4
                case ReefLevel.L4.value:
                    return 5

async def calc_auto_reef_score_by_side_abs(team_number: str, side: str):
    converted_side = convert_auto_reef_side_to_pos(side)
    print(converted_side)
    point_value = get_reef_level_score_weight(side, "auto")
    print (point_value)
    matches = await get_path(team_number, "auto")  # Fetch paths

    # Check if paths is empty
    if not matches:
        return 0  # Return default value when no paths are present

    filtered_matches = []

    for paths in matches:
        side_matched = []
        for single_path in paths["path"]:
            for pos in converted_side:
                if single_path.get("point") == pos:
                    side_matched.append(paths)
                    break
        print(side_matched)
        filtered_matches.append(side_matched)

    side_scores = []

    for match in filtered_matches:
        if not match:
            side_scores.append(0)
            continue

        for paths in match:
            score = 0
            for single_path in paths["path"]:
                for level in ALL_REEF_LEVELS:
                    d_score = get_reef_level_score_weight(level, "auto")
                    for pos in convert_reef_level_to_pos(level):
                        if single_path.get("point") == pos:
                            score += d_score
                            break
            side_scores.append(score)

    return get_abs_team_stats(side_scores)  # Compute stats if side_matched has values

async def calc_auto_reef_score_by_side_rel(team_number: str, side: str):
    unsorted_data = await result_collection.find(
        {},  # Query criteria
        {
            "_id": 0,
            "team_number": 1,
            side: f"$auto.reef_score_by_side.{side}.average"
        }
    ).to_list(None)

    data = sorted(unsorted_data, key=itemgetter(side), reverse=True)

    return calc_relative(team_number, data, side)

async def calc_reef_success_rate_by_side(team_number: str, side: str, period: str = "auto"):
    converted_side = convert_auto_reef_side_to_pos(side)
    matches_paths = await get_path(team_number, period)

    matched = 0
    count_succeeded = 0

    for paths in matches_paths:
        for single_path in paths["path"]:
            for pos in converted_side:
                if single_path.get("point") == pos:
                    matched += 1
                    if single_path.get("success"):
                        count_succeeded += 1
                    break

    if matched == 0:  # Avoid division by zero
        return 0.0

    rate = count_succeeded / matched

    return rate

async def count_processor_score_abs(team_number: str, period: str):
    match_paths = await get_path(team_number, period)

    # Safety check in case get_path returns None or invalid data
    if not match_paths:
        return {
            "abs_team_stats": {},  # Default empty stats if no paths are found
            "rel_team_stats": await get_rel_team_stats(team_number, "processor", period)
        }

    processor_score = []

    for paths in match_paths:
        score = 0
        for single_path in paths["path"]:
            if period == "auto" and single_path.get("point") == "processor" and single_path.get("success"):
                score += 6
            elif period == "teleop" and single_path.get("point") == "processor":
                score += 6
        processor_score.append(score)

    # print (processor_score)
    # Ensure processor_score is not empty before calculating stats
    if not processor_score:
        return {"average": 0, "stability": 0}

    # print({"count_processor_score": {**abs_team_stats, **rel_team_stats}})

    return get_abs_team_stats(processor_score)

async def calc_processor_score_rel(team_number: str, period: str):
    return await get_rel_team_stats(team_number, "processor_score", period)

async def count_net_score_abs(team_number: str, period: str):
    matches = await get_path(team_number, period)

    # Check if paths is empty or invalid:
    if not matches:
        # Return default stats if no paths are found
        return {
            "max": 0,
            "min": 0,
            "average": 0,
            "count": 0,
            # Add any other relevant default statistics here
        }

    net_score = []

    for paths in matches:
        score = 0
        for path in paths["path"]:
            # Default to False if no "success" key
            match period:
                case "auto":
                    if path.get("point") == "net" and path.get("success"):
                        score += 4
                case "teleop":
                    if path.get("point") == "net":
                        score += 4
        net_score.append(score)

    # Ensure net_score is not empty before proceeding:
    if not net_score:
        return {
            "max": 0,
            "min": 0,
            "average": 0,
            "count": 0,
            # Add any other relevant default statistics here
        }

    # Compute stats if net_score has data
    return get_abs_team_stats(net_score)

async def calc_net_score_rel(team_number: str, period: str):
    return await get_rel_team_stats(team_number, "net_score", period)

async def calc_auto_reef_point_count_abs(team_number: str, pos: str):
    matches = await get_path(team_number, "auto")

    matched_per_match = []

    for paths in matches:
        count = 0
        for single_path in paths["path"]:
            if single_path.get("point") == pos and single_path.get("success"):
                count += 1

        matched_per_match.append(count)

    print({f"calc_auto_reef_point_count_abs-{pos}": matched_per_match})

    if not matched_per_match:
        return {"average": 0.0, "stability": 0.0}


    return get_abs_team_stats(matched_per_match)

async def calc_auto_reef_point_count_rel (team_number: str, pos: str):
    unsorted_data = await result_collection.find(
        {},  # Query criteria
        {
            "_id": 0,
            "team_number": 1,
            pos: f"$auto.reef_count_per_point.{pos}.average"
        }
    ).to_list(None)

    for item in unsorted_data:
        if pos not in item:
            team_number_temp = item.get("team_number")
            unsorted_data.remove(item)
            unsorted_data.append({"team_number": team_number_temp, pos: 0.0})

    print ({"calc_auto_reef_point_count_rel": unsorted_data})
    data = sorted(unsorted_data, key=itemgetter(pos), reverse=True)

    return calc_relative(team_number, data, pos)

async def pack_auto_data_abs(team_number: str):
    data = {
        "preload_count": await count_preload(team_number),
        "start_position_count": await count_start_pos(team_number),
        "leave_success_rate": await calc_leave_success_rate(team_number),
        "reef": {
            "l1": {** await calc_auto_reef_level_abs(team_number, ReefLevel.L1.value)},
            "l2": {** await calc_auto_reef_level_abs(team_number, ReefLevel.L2.value)},
            "l3": {** await calc_auto_reef_level_abs(team_number, ReefLevel.L3.value)},
            "l4": {** await calc_auto_reef_level_abs(team_number, ReefLevel.L4.value)},

        },
        "reef_count_per_point":{
            "l1ReefAB": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefAB")},
            "l1ReefCD": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefCD")},
            "l1ReefEF": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefEF")},
            "l1ReefGH": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefGH")},
            "l1ReefIJ": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefIJ")},
            "l1ReefKL": {** await calc_auto_reef_point_count_abs(team_number, "l1ReefKL")},
            "l2ReefAB": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefAB")},
            "l2ReefCD": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefCD")},
            "l2ReefEF": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefEF")},
            "l2ReefGH": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefGH")},
            "l2ReefIJ": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefIJ")},
            "l2ReefKL": {** await calc_auto_reef_point_count_abs(team_number, "l2ReefKL")},
            "l3ReefAB": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefAB")},
            "l3ReefCD": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefCD")},
            "l3ReefEF": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefEF")},
            "l3ReefGH": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefGH")},
            "l3ReefIJ": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefIJ")},
            "l3ReefKL": {** await calc_auto_reef_point_count_abs(team_number, "l3ReefKL")},
            "l4ReefAB": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefAB")},
            "l4ReefCD": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefCD")},
            "l4ReefEF": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefEF")},
            "l4ReefGH": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefGH")},
            "l4ReefIJ": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefIJ")},
            "l4ReefKL": {** await calc_auto_reef_point_count_abs(team_number, "l4ReefKL")}
        },
        "reef_success_rate_by_side": {
            "AB": await calc_reef_success_rate_by_side(team_number, ReefSide.AB.value, "auto"),
            "CD": await calc_reef_success_rate_by_side(team_number, ReefSide.CD.value, "auto"),
            "EF": await calc_reef_success_rate_by_side(team_number, ReefSide.EF.value, "auto"),
            "GH": await calc_reef_success_rate_by_side(team_number, ReefSide.GH.value, "auto"),
            "IJ": await calc_reef_success_rate_by_side(team_number, ReefSide.IJ.value, "auto"),
            "KL": await calc_reef_success_rate_by_side(team_number, ReefSide.KL.value, "auto")
        },
        "reef_score_by_side": {
            "AB": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.AB.value)},
            "CD": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.CD.value)},
            "EF": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.EF.value)},
            "GH": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.GH.value)},
            "IJ": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.IJ.value)},
            "KL": {**await calc_auto_reef_score_by_side_abs(team_number, ReefSide.KL.value)}
        },
        "reef_score": {**await calc_auto_reef_score_abs(team_number)},
        "processor_score": {**await count_processor_score_abs(team_number, "auto")},
        "net_score": {**await count_net_score_abs(team_number, "auto")}
    }
    print({"pack_auto_data_abs": data})
    return data

async def pack_auto_data_rel(team_number: str):
    data = {
        "reef": {
            "l1": await calc_reef_level_rel(team_number, ReefLevel.L1.value, "auto"),
            "l2": await calc_reef_level_rel(team_number, ReefLevel.L2.value, "auto"),
            "l3": await calc_reef_level_rel(team_number, ReefLevel.L3.value, "auto"),
            "l4": await calc_reef_level_rel(team_number, ReefLevel.L4.value, "auto")
        },
        "reef_count_per_point": {
            "l1ReefAB": await calc_auto_reef_point_count_rel(team_number, "l1ReefAB"),
            "l1ReefCD": await calc_auto_reef_point_count_rel(team_number, "l1ReefCD"),
            "l1ReefEF": await calc_auto_reef_point_count_rel(team_number, "l1ReefEF"),
            "l1ReefGH": await calc_auto_reef_point_count_rel(team_number, "l1ReefGH"),
            "l1ReefIJ": await calc_auto_reef_point_count_rel(team_number, "l1ReefIJ"),
            "l1ReefKL": await calc_auto_reef_point_count_rel(team_number, "l1ReefKL"),
            "l2ReefAB": await calc_auto_reef_point_count_rel(team_number, "l2ReefAB"),
            "l2ReefCD": await calc_auto_reef_point_count_rel(team_number, "l2ReefCD"),
            "l2ReefEF": await calc_auto_reef_point_count_rel(team_number, "l2ReefEF"),
            "l2ReefGH": await calc_auto_reef_point_count_rel(team_number, "l2ReefGH"),
            "l2ReefIJ": await calc_auto_reef_point_count_rel(team_number, "l2ReefIJ"),
            "l2ReefKL": await calc_auto_reef_point_count_rel(team_number, "l2ReefKL"),
            "l3ReefAB": await calc_auto_reef_point_count_rel(team_number, "l3ReefAB"),
            "l3ReefCD": await calc_auto_reef_point_count_rel(team_number, "l3ReefCD"),
            "l3ReefEF": await calc_auto_reef_point_count_rel(team_number, "l3ReefEF"),
            "l3ReefGH": await calc_auto_reef_point_count_rel(team_number, "l3ReefGH"),
            "l3ReefIJ": await calc_auto_reef_point_count_rel(team_number, "l3ReefIJ"),
            "l3ReefKL": await calc_auto_reef_point_count_rel(team_number, "l3ReefKL"),
            "l4ReefAB": await calc_auto_reef_point_count_rel(team_number, "l4ReefAB"),
            "l4ReefCD": await calc_auto_reef_point_count_rel(team_number, "l4ReefCD"),
            "l4ReefEF": await calc_auto_reef_point_count_rel(team_number, "l4ReefEF"),
            "l4ReefGH": await calc_auto_reef_point_count_rel(team_number, "l4ReefGH"),
            "l4ReefIJ": await calc_auto_reef_point_count_rel(team_number, "l4ReefIJ"),
            "l4ReefKL": await calc_auto_reef_point_count_rel(team_number, "l4ReefKL")
        },
        "reef_score_by_side": {
            "AB": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.AB.value),
            "CD": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.CD.value),
            "EF": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.EF.value),
            "GH": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.GH.value),
            "IJ": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.IJ.value),
            "KL": await calc_auto_reef_score_by_side_rel(team_number, ReefSide.KL.value)
        },
        "reef_score": await calc_auto_reef_score_rel(team_number),
        "processor_score": await calc_processor_score_rel(team_number, "auto"),
        "net_score": await calc_net_score_rel(team_number, "auto")
    }
    print ({"pack_auto_data_rel": data})
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

    if cycle_type == "coral":
        start_pos.extend([
            TeleopPathPoint.GROUND_CORAL.value,
            TeleopPathPoint.CORAL_STATION.value
        ])
        end_pos.extend([
            TeleopPathPoint.L1_REEF.value,
            TeleopPathPoint.L2_REEF.value,
            TeleopPathPoint.L3_REEF.value,
            TeleopPathPoint.L4_REEF.value
        ])
    elif cycle_type == "algae":
        start_pos.extend([
            TeleopPathPoint.REEF_ALGAE.value,
            TeleopPathPoint.GROUND_ALGAE.value
        ])
        end_pos.extend([
            TeleopPathPoint.NET.value,
            TeleopPathPoint.PROCESSOR.value
        ])

    print (start_pos, end_pos)
    # Filter the data for start and end points
    start_points = []
    end_points = []

    for match in data:
        for point in match["path"]:
            if point["point"] in start_pos:
                start_points.append(point["timestamp"])
            elif point["point"] in end_pos:
                end_points.append(point["timestamp"])

    cycle_time = []

    i, j = 0, 0
    n, m = len (start_points), len (end_points)

    while i < n and j < m:
        if start_points[i] < end_points[j]:
            cycle_time.append(end_points[j] - start_points[i])
            i += 1
            j += 1
        else:
            j += 1

    return cycle_time

async def calc_cycle_time_abs(team_number: str, cycle_type: str):
    data = await get_path(team_number, "teleop")
    print (data)
    cycle_times = search_cycle_time(data, cycle_type)

    if not cycle_times:
        # Handle empty cycle_times by returning default values
        return {"average": 0, "stability": 0}

    return get_abs_team_stats(cycle_times)

async def calc_cycle_time_rel(team_number: str, cycle_type: str):
    unsorted_data = await result_collection.find(
        {},  # Query criteria
        {
            "_id": 0,
            "team_number": 1,
            cycle_type: f"$teleop.cycle_time.{cycle_type}.average"
        }
    ).to_list(None)

    data = sorted(unsorted_data, key=itemgetter(cycle_type), reverse=True)
    return calc_relative(team_number, data, cycle_type)

async def count_hang_abs(team_number):
    data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "hang_time": "$teleop.hang_time"
        }
    ).to_list(None)
    print (data)
    hang_time = [item.get("hang_time") for item in data]
    print  (hang_time)
    # Handle empty hang_time case
    if not hang_time:  # If hang_time is an empty list
        return {"average": 0, "stability": 0}

    # print({"calc_cycle_time": {**abs_stats, **rel_stats}})
    return get_abs_team_stats(hang_time)

async def calc_hang_rel(team_number: str):
    return await get_rel_team_stats(team_number, "hang", "teleop")

async def pack_teleop_data_abs(team_number: str):
    data = {
        "reef": {
            "l1": {**await calc_teleop_reef_level_abs(team_number, ReefLevel.L1.value)},
            "l2": {**await calc_teleop_reef_level_abs(team_number, ReefLevel.L2.value)},
            "l3": {**await calc_teleop_reef_level_abs(team_number, ReefLevel.L3.value)},
            "l4": {**await calc_teleop_reef_level_abs(team_number, ReefLevel.L4.value)},

        },
        "processor_score": {**await count_processor_score_abs(team_number, "teleop")},
        "net_score": {**await count_net_score_abs(team_number, "teleop")},
        "cycle_time": {
            "coral": {**await calc_cycle_time_abs(team_number, "coral")},
            "algae": {**await calc_cycle_time_abs(team_number, "algae")}
        },
        "hang": {**await count_hang_abs(team_number)}
    }
    print({"pack_teleop_data": data})
    return data

async def pack_teleop_data_rel(team_number: str):
    data = {
        "reef": {
            "l1": {**await calc_reef_level_rel(team_number, ReefLevel.L1.value, "teleop")},
            "l2": {**await calc_reef_level_rel(team_number, ReefLevel.L2.value, "teleop")},
            "l3": {**await calc_reef_level_rel(team_number, ReefLevel.L3.value, "teleop")},
            "l4": {**await calc_reef_level_rel(team_number, ReefLevel.L4.value, "teleop")}
        },
        "processor_score": {**await calc_processor_score_rel(team_number, "teleop")},
        "net_score": {**await calc_net_score_rel(team_number, "teleop")},
        "cycle_time": {
            "coral": {**await calc_cycle_time_rel(team_number, "coral")},
            "algae": {**await calc_cycle_time_rel(team_number, "algae")}
        },
        "hang": {**await calc_hang_rel(team_number)}
    }
    print ({"pack_teleop_data_rel": data})
    return data


async def get_comments(team_number: str):
    # Get all documents matching the query and project only the 'comments' field
    comments = await raw_collection.find(
        {"team_number": team_number},
        {"_id": 0, "comment": 1}  # Fixed projection syntax
    ).to_list(None) # Convert the cursor to a list

    comments_raw = [item.get("comment") for item in comments]

    return comments_raw  # Return the list of comments

async def count_bypassed(team_number: str):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "bypassed": 1
        }
    ).to_list(None)
    count = raw_data.count({"bypassed": True})
    print({"count_bypassed": count})
    return count

async def count_disabled(team_number: str):
    raw_data = await raw_collection.find(
        {"team_number": team_number},
        {
            "_id": 0,
            "disabled": 1
        }
    ).to_list(None)
    count = raw_data.count({"disabled": True})
    print({"count_disabled": count})
    return count

async def pack_obj_data_abs(team_number: str):
    data = {
        "team_number": team_number,
        "auto": await pack_auto_data_abs(team_number),
        "teleop": await pack_teleop_data_abs(team_number),
        "bypassed_count": await count_bypassed(team_number),
        "disabled_count": await count_disabled(team_number),
        "comment": await get_comments(team_number)
    }
    print({"pack_data": data})
    return data

async def pack_obj_data_rel(team_number: str):
    data = {
        "team_number": team_number,
        "auto": await pack_auto_data_rel(team_number),
        "teleop": await pack_teleop_data_rel(team_number),
    }
    print({"pack_data": data})
    return data

async def post_obj_results(team_number: str):
    obj = {**await pack_obj_data_abs(team_number)}
    rel = {**await pack_obj_data_rel(team_number)}

    post_data = merge_data(obj, rel)

    await result_collection.update_one({"team_number": team_number}, {"$set": post_data}, upsert=True)

    return {"message": "Data posted successfully"}

async def refresh_all_obj_results():
    team_set = await get_all_teams()
    print (team_set)
    if '' in team_set:
        team_set.remove('')

    for team in team_set:
        await post_obj_results(team)

    return {"message": "Data refreshed successfully"}


def merge_data(data1: dict, data2: dict):
    """
    合併兩個巢狀字典，對於相同的鍵，若值為字典則遞迴合併，否則使用 dict2 的值。
    """
    for key in data2:
        if key in data1:
            # 如果鍵存在且都是字典，則遞迴合併
            if isinstance(data1[key], dict) and isinstance(data2[key], dict):
                merge_data(data1[key], data2[key])
            else:
                # 否則使用 dict2 的值覆蓋 dict1 的值
                data1[key] = data2[key]
        else:
            # 如果鍵不存在於 dict1，則直接添加
            data1[key] = data2[key]

    return data1