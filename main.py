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

class Url(BaseModel):
    url: str

@app.post("/api/")
async def optimize_url(url: Url):
    # Do something with the url data
    destinations, base_url, directories = qs_parser(url.url)
    plan_output, distance = main(destinations)
    solution_url = qs_constructor(destinations, base_url, directories, plan_output)
    return {
        "url": url.url,
        "destinations": destinations,
        "base_url": base_url,
        "directories": directories,
        "plan_output": plan_output,
        "distance": distance,
        "solution_url": solution_url
    }