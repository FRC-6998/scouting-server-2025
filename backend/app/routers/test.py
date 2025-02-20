from fastapi import APIRouter

from backend.app.scripts.objective_calculate import count_hang_abs, post_obj_results, calc_reef_level_rel

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test(team_number: str, level: str, period: str):
    await calc_reef_level_rel(team_number, level, period)
    return {"message": "Test successful"}
