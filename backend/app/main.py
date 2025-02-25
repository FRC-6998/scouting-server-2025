from fastapi import FastAPI

from .routers import objective_scout, subjective_scout, pit_scout, test
from .scripts.objective_calculate import raw_collection

scouting_app = FastAPI(
    title="Scouting Field Server API",
    description="API for Scouting Field Server made by Team Unipards 6998",
    version="0.2.0-alpha",
)

scouting_app.include_router(objective_scout.router)
scouting_app.include_router(subjective_scout.router)
scouting_app.include_router(pit_scout.router)
scouting_app.include_router(test.router)

@scouting_app.get(
    "/team_list",
    name="Getting team list",
    description="Getting team list from the database.",
    response_description="Got team list successfully",
)
async def get_team_list(match_level: str, match_number: str):
    dict_data = await raw_collection.find(
        {"match_level": match_level, "match_number": match_number},
        {"_id":0, "team_number":1}
    ).to_list(None)
    list_data = list(d["team_number"] for d in dict_data)
    print (list_data)
    return {"teams": list_data}