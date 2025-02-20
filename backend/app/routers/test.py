from fastapi import APIRouter

from backend.app.scripts.objective_calculate import count_hang

router = APIRouter(
    prefix= "/test"
)

reef_levels = ["l1", "l2", "l3", "l4"]


@router.get("/")
async def test(team_number: str):
    await post_obj_results(team_number)
    return {"message": "Test successful"}
