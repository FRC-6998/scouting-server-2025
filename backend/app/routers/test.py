from fastapi import APIRouter

from backend.app.scripts.objective_calculate import calc_reef_level

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test():
    test_list = [await calc_reef_level("6998", level, "auto") for level in reef_levels]
    print (test_list)
    return test_list
