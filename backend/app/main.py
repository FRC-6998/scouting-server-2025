from fastapi import FastAPI

from .routers import objective_scout, subjective_scout, pit_scout, test

scouting_app = FastAPI(
    title="Scouting Field Server API",
    description="API for Scouting Field Server made by Team Unipards 6998",
    version="0.1.0",
)

scouting_app.include_router(objective_scout.router)
scouting_app.include_router(subjective_scout.router)
scouting_app.include_router(pit_scout.router)
scouting_app.include_router(test.router)
