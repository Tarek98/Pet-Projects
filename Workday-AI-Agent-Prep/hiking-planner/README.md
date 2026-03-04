# Hiking Trip Planner

Multi-agent workflow: geocode → (weather + trails + ETA in parallel) → planner. Suggests trails near your home, weather, drive time, and drafts a social post to invite friends.

**Stack:** LangGraph, LangChain, Anthropic; Nominatim + Open-Meteo (no keys); mock AllTrails/ETA.

## Setup

```bash
cd Workday-AI-Agent-Prep/hiking-planner
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
# Add .env with ANTHROPIC_API_KEY
```

## CLI

```bash
python hiking_planner.py
```

## API + Web UI

1. **API:** `uvicorn hiking_api:app --reload --port 8000`
2. **UI:** `cd hiking-planner-ui && npm install && npm run dev` → http://localhost:5173

See `hiking-planner-ui/README.md` for details.
