from operator import itemgetter

import numba
import numpy as np

from ..constants import SUBJECTIVE_RAW_COLLECTION, SUBJECTIVE_RESULT_COLLECTION
from ..scripts.initdb import init_collection

subjective_raw = init_collection(SUBJECTIVE_RAW_COLLECTION)
subjective_result = init_collection(SUBJECTIVE_RESULT_COLLECTION)


async def get_team_datas(team_number: int, key: str):
    data = [
        await subjective_raw.find(
            {"team1.team_number": team_number},
            {
                "_id": 0,
                key: "$team1." + key
            },
        ),
        await subjective_raw.find(
            {"team2.team_number": team_number},
            {
                "_id": 0,
                key: "$team2." + key
            },
        ),
        await subjective_raw.find(
            {"team3.team_number": team_number},
            {
                "_id": 0,
                key: "$team3." + key
            },
        ),
    ]
    return data


@numba.jit(cache=True)
def analysis_absolute(data: list[dict], key: str):
    data_np = np.array([])
    for i in data:
        data_np = np.append(data_np, i[key])

    average = np.mean(data_np)
    stability = average / np.std(data_np)
    return {"average": average, "stability": stability}


async def analysis_relative(team_number: int, key: str, is_descending: bool = False):
    unsorted_data = [
        await subjective_result.find(
            {},
            {
                "_id": 0,
                "team_number": 1,
                key: 1
            }
        )
    ]
    data = sorted(unsorted_data, key=itemgetter(key),
                  reverse=is_descending)  # Cus less is better
    return calc_relative(team_number, data, key)


@numba.jit(cache=True)
def calc_relative(team_number: int, data: list, key: str):
    rank = 0
    for i in data:
        if i["team_number"] == team_number:
            rank = i[key]
            break

    data_np = np.array(d[rank-1] for d in data)
    z_score = (data_np[rank-1] - np.mean(data_np)) / np.std(data_np)

    return {"rank": rank, "z_score": z_score}


async def get_driver_awareness(team_number: int):
    data = await get_team_datas(team_number, "driver_awareness")
    return analysis_absolute(data) | await analysis_relative(team_number, "driver_awareness", False)


async def get_coral_station_awareness(team_number: int):
    data = await get_team_datas(team_number, "coral_station_awareness")
    return analysis_absolute(data) | await analysis_relative(team_number, "coral_station_awareness", False)


async def get_num_score_on_net(team_number: int):
    data = await get_team_datas(team_number, "num_score_on_net")
    return analysis_absolute(data) | await analysis_relative(team_number, "num_score_on_net", True)


async def get_mobility(team_number: int):
    data = await get_team_datas(team_number, "mobility")
    return analysis_absolute(data) | await analysis_relative(team_number, "mobility", False)


async def get_defense(team_number: int):
    data = await get_team_datas(team_number, "defense")
    return analysis_absolute(data) | await analysis_relative(team_number, "defense", False)


async def pack_result(team_number: int):
    return {
        "team_number": team_number,
        "driver_awareness": await get_driver_awareness(team_number),
        "coral_station_awareness": await get_coral_station_awareness(team_number),
        "num_score_on_net": await get_num_score_on_net(team_number),
        "mobility": await get_mobility(team_number),
        "defense": await get_defense(team_number),
    }


async def post_sbj_results(team_number: int):
    data = await pack_result(team_number)
    await subjective_result.insert_one(data, bypass_document_validation=False, session=None)
