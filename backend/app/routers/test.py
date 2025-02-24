from fastapi import APIRouter

from backend.app.scripts.objective_calculate import count_hang_abs, post_obj_results, calc_reef_level_rel, \
    refresh_all_obj_results

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test():
    return await refresh_all_obj_results()
