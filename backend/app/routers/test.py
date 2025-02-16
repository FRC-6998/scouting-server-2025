from fastapi import APIRouter

from backend.app.scripts.objective_calculate import calc_reef_level_objective, calc_reef_score

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test():
    print (await calc_reef_score("6998", "auto"))
    return
