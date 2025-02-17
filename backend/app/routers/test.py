from fastapi import APIRouter

from backend.app.scripts.objective_calculate import calc_reef_success_rate_by_side, count_processor_score

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test(team_number: str = None):
    print (await count_processor_score(team_number, "teleop"))
    return {"message": "Tested successfully"}
