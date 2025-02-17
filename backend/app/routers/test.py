from fastapi import APIRouter

from backend.app.scripts.objective_calculate import calc_auto_reef_score_by_side

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test():
    print (await calc_auto_reef_score_by_side("6998", "IJ"))
    return {"message": "Tested successfully"}
