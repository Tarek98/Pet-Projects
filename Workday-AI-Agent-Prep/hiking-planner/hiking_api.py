"""
FastAPI server for the Hiking Trip Planner.
POST /api/plan with { "home_address": "...", "hike_start": "Saturday 9:00 AM" }.
Run: uvicorn hiking_api:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv(override=True)

# Lazy import so we only load LangGraph when the app starts
_plan_result: str | None = None


def _run_plan_sync(home_address: str, hike_start: str) -> str:
    from hiking_planner import run_plan
    return run_plan(home_address, hike_start)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # optional cleanup
    pass


app = FastAPI(title="Hiking Trip Planner API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    home_address: str
    hike_start: str = ""


class PlanResponse(BaseModel):
    output: str


@app.post("/api/plan", response_model=PlanResponse)
async def plan(request: PlanRequest):
    """Run the hiking planner and return trip summary + social post."""
    if not request.home_address.strip():
        raise HTTPException(status_code=400, detail="home_address is required")
    try:
        import asyncio
        output = await asyncio.to_thread(
            _run_plan_sync,
            request.home_address.strip(),
            request.hike_start.strip(),
        )
        return PlanResponse(output=output)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
