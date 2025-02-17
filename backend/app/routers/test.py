from fastapi import APIRouter

from backend.app.scripts.objective_calculate import count_net_score, search_cycle_time, calc_cycle_time

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test(team_number: str, cycle_type: str):
    print (await calc_cycle_time(team_number, cycle_type))
    return {"message": "Tested successfully"}
