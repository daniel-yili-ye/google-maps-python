from typing import Union
from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tsp_solver import TSPSolver

app = FastAPI()

# Allow all CORS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteInfo(BaseModel):
    url: str
    travel_mode: str
    fixed_start_point: str | None
    fixed_end_point: str | None


@app.post("/api/")
async def optimize_url(route_info: RouteInfo):
    # Do something with the url data
    optimized_url = TSPSolver(route_info)
    optimized_url.solver('duration_matrix')
    optimized_url.qs_constructor()

    return {
        "old_url": optimized_url.old_url,
        "new_url": optimized_url.new_url,
        "distance_diff": optimized_url.distance_diff,
        "duration_diff": optimized_url.duration_diff,
    }
