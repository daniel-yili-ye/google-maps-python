from typing import Union
from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tsp_solver import main
from qs_parser import qs_parser
from qs_constructor import qs_constructor

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
    destinations, base_url, directories = qs_parser(route_info.url)
    plan_output, distance, data = main(destinations, route_info)
    solution_url, solution = qs_constructor(
        destinations, base_url, directories, plan_output, data)
    return {
        "url": route_info.url,
        "destinations": destinations,
        "distance": distance,
        "solution_url": solution_url,
        "solution": solution
    }
