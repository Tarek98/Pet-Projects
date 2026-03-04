"""
Hiking Trip Planner — multi-agent workflow.
Uses real geocoding (Nominatim) + weather (Open-Meteo); mock AllTrails-style trails and ETA from home to trail.
Flow: Geocode → (Weather + Trails in parallel) → Planner (itinerary + social post).
Run from hiking-planner/: pip install -r requirements.txt && python hiking_planner.py
Requires: .env with ANTHROPIC_API_KEY
"""
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Annotated, TypedDict

import httpx
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate

load_dotenv(override=True)

USER_AGENT = "HikingPlannerDemo/1.0 (learning project)"


# --- Real APIs (no keys required) ---

@tool
def geocode_address(
    address: Annotated[str, "Full address or city, e.g. '123 Main St, Vancouver, BC' or 'Seattle, WA'"],
) -> str:
    """Convert a home address or city name into latitude and longitude and a display name. Use this first to get coordinates for weather and to describe the area for trail search."""
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
            r = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1},
            )
            r.raise_for_status()
            data = r.json()
            if not data:
                return f"No results for: {address}"
            d = data[0]
            lat, lon = d["lat"], d["lon"]
            name = d.get("display_name", address)
            return f"Coordinates for '{address}': lat={lat}, lon={lon}. Display name: {name}. Use lat/lon for get_weather and the city/area name for search_trails_near."
    except Exception as e:
        return f"Geocoding failed: {e}"


def _geocode_raw(address: str) -> dict | None:
    """Return {lat, lon, region} or None if geocoding fails. Used by graph nodes."""
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
            r = client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": address, "format": "json", "limit": 1},
            )
            r.raise_for_status()
            data = r.json()
            if not data:
                return None
            d = data[0]
            lat, lon = float(d["lat"]), float(d["lon"])
            region = d.get("display_name", address)
            return {"lat": lat, "lon": lon, "region": region}
    except Exception:
        return None


@tool
def get_weather(
    latitude: Annotated[float, "Latitude from geocode_address"],
    longitude: Annotated[float, "Longitude from geocode_address"],
) -> str:
    """Get current and 7-day forecast (max/min temp, precipitation) for a location. Use coordinates from geocode_address."""
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,weather_code,precipitation",
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                    "timezone": "auto",
                },
            )
            r.raise_for_status()
            data = r.json()
            cur = data.get("current", {})
            daily = data.get("daily", {})
            days = daily.get("time", [])[:3]
            maxs = daily.get("temperature_2m_max", [])[:3]
            mins = daily.get("temperature_2m_min", [])[:3]
            prec = daily.get("precipitation_sum", [])[:3]
            lines = [
                f"Current: {cur.get('temperature_2m', 'N/A')}°C, precipitation {cur.get('precipitation', 0)} mm.",
                "Next 3 days:",
            ]
            for i, day in enumerate(days):
                lines.append(f"  {day}: max {maxs[i] if i < len(maxs) else 'N/A'}°C, min {mins[i] if i < len(mins) else 'N/A'}°C, precip {prec[i] if i < len(prec) else 'N/A'} mm")
            return "\n".join(lines)
    except Exception as e:
        return f"Weather fetch failed: {e}"


# --- Mock AllTrails-style and Google Maps (replace with real APIs when you have keys) ---

def _mock_trails(region: str) -> str:
    """Simulated trail list; in production you'd call AllTrails or similar."""
    trails = [
        {"name": "Lynn Canyon Loop", "difficulty": "moderate", "length_km": 5.2, "rating": 4.6, "drive_min": 25},
        {"name": "Grouse Grind", "difficulty": "hard", "length_km": 2.9, "rating": 4.5, "drive_min": 30},
        {"name": "Pacific Spirit Park", "difficulty": "easy", "length_km": 8.0, "rating": 4.4, "drive_min": 15},
        {"name": "Quarry Rock", "difficulty": "moderate", "length_km": 3.8, "rating": 4.7, "drive_min": 35},
        {"name": "Lighthouse Park", "difficulty": "easy", "length_km": 4.5, "rating": 4.8, "drive_min": 40},
    ]
    lines = [f"Trails near {region} (mock data; real app would use AllTrails API):"]
    for t in trails:
        lines.append(f"  - {t['name']}: {t['difficulty']}, {t['length_km']} km, rating {t['rating']}, ~{t['drive_min']} min drive")
    return "\n".join(lines)


@tool
def search_trails_near(
    region_or_city: Annotated[str, "City or region name, e.g. from geocode_address display name"],
    max_drive_minutes: Annotated[int, "Max drive time from home in minutes, e.g. 45"] = 45,
) -> str:
    """Search for hiking trails near a region. Returns trail name, difficulty, length, rating, and approximate drive time. (Uses mock data; real implementation would use AllTrails or similar.)"""
    return _mock_trails(region_or_city)


def _parse_arrival_and_leave_by(arrival_day_time: str, drive_minutes: int) -> str:
    """Parse a time string like '9:00 AM' or 'Saturday 9:00 AM' and return 'Leave by ~H:MM AM/PM'."""
    # Match hour, optional minute, optional am/pm (case insensitive).
    m = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", arrival_day_time.strip(), re.I)
    if not m:
        return ""
    hour = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) else 0
    ampm = (m.group(3) or "am").lower()
    if ampm == "pm" and hour != 12:
        hour += 12
    elif ampm == "am" and hour == 12:
        hour = 0
    total_mins = hour * 60 + minute
    leave_mins = total_mins - drive_minutes
    if leave_mins < 0:
        leave_mins += 24 * 60
    lh, lm = divmod(leave_mins, 60)
    if lh == 0:
        lh = 12
        suffix = "AM"
    elif lh < 12:
        suffix = "AM"
    elif lh == 12:
        suffix = "PM"
    else:
        lh -= 12
        suffix = "PM"
    return f"Leave by ~{lh}:{lm:02d} {suffix}"


@tool
def get_eta_home_to_trail(
    from_address: Annotated[str, "User's home address"],
    to_trail: Annotated[str, "Trail name or trailhead, e.g. 'Lynn Canyon Loop trailhead'"],
    arrival_day_time: Annotated[
        str | None,
        "Desired arrival at trail, e.g. 'Saturday 9:00 AM'. Used to compute when to leave home.",
    ] = None,
) -> str:
    """Get estimated drive time from home to trailhead and, if arrival time is given, when to leave home to arrive on time. (Mock; real implementation would use Google Maps API.)"""
    mock_minutes = {"Pacific Spirit": 15, "Lynn Canyon": 25, "Grouse": 30, "Quarry Rock": 35, "Lighthouse": 40}
    mins = 25
    for key, m in mock_minutes.items():
        if key.lower() in to_trail.lower():
            mins = m
            break
    msg = f"ETA from home to {to_trail}: ~{mins} min drive."
    if arrival_day_time and arrival_day_time.strip():
        leave_by = _parse_arrival_and_leave_by(arrival_day_time, mins)
        if leave_by:
            msg += f" To arrive by {arrival_day_time.strip()}, {leave_by}."
    msg += " (Mock; use Google Maps API for real ETA.)"
    return msg


# --- Multi-agent graph ---

class HikingState(TypedDict, total=False):
    input: str
    arrival_day_time: str
    lat: float
    lon: float
    region: str
    research: str
    output: str


def _geocode_node(state: HikingState) -> dict:
    """Resolve address to coordinates and region. Must run before parallel research."""
    geo = _geocode_raw(state["input"] or "")
    if not geo:
        return {"research": f"Geocoding failed for: {state.get('input', '')}"}
    return {"lat": geo["lat"], "lon": geo["lon"], "region": geo["region"]}


def _research_parallel_node(state: HikingState) -> dict:
    """Run weather, trail search, and ETA from home in parallel (no LLM)."""
    lat, lon = state.get("lat"), state.get("lon")
    region = state.get("region") or "unknown"
    address = state.get("input") or ""
    arrival = state.get("arrival_day_time") or ""

    if lat is None or lon is None:
        return {"research": state.get("research", "Missing coordinates.")}

    def run_weather():
        return get_weather.invoke({"latitude": lat, "longitude": lon})

    def run_trails():
        return search_trails_near.invoke({"region_or_city": region, "max_drive_minutes": 45})

    def run_eta():
        return get_eta_home_to_trail.invoke({
            "from_address": address,
            "to_trail": "Pacific Spirit Park trailhead",
            "arrival_day_time": arrival.strip() or None,
        })

    parts = []
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(run_weather), ex.submit(run_trails), ex.submit(run_eta)]
        for fut in as_completed(futs):
            try:
                parts.append(fut.result())
            except Exception as e:
                parts.append(f"Error: {e}")

    research = "\n\n".join(parts)
    return {"research": research}


def _planner_node(state: HikingState) -> dict:
    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.3)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a trip planner and social media writer. Given the RESEARCH below (trails, weather, ETA from home to trail), produce two things in your response, clearly labeled:

1) TRIP SUMMARY: A short itinerary (which trail(s), when to go, what to bring based on weather, and drive time from home).
2) SOCIAL POST: A friendly, inviting social media post (Instagram or Facebook style) to invite friends to join the hike. Include emoji, trail name, date suggestion, and a call to action (e.g. "Who's in?"). Keep the post concise and fun."""),
        ("human", "User request: {input}\nDesired arrival at trail: {arrival_day_time}\n\nResearch:\n{research}"),
    ])
    chain = prompt | llm
    response = chain.invoke({
        "input": state["input"],
        "arrival_day_time": state.get("arrival_day_time") or "not specified",
        "research": state["research"],
    })
    out = response.content if hasattr(response, "content") else str(response)
    return {"output": out}


def get_graph():
    """Build and return the compiled LangGraph. Requires ANTHROPIC_API_KEY."""
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY not set")
    from langgraph.graph import StateGraph, START, END

    workflow = StateGraph(HikingState)
    workflow.add_node("geocode", _geocode_node)
    workflow.add_node("research_parallel", _research_parallel_node)
    workflow.add_node("planner", _planner_node)
    workflow.add_edge(START, "geocode")
    workflow.add_edge("geocode", "research_parallel")
    workflow.add_edge("research_parallel", "planner")
    workflow.add_edge("planner", END)
    return workflow.compile()


def run_plan(home_address: str, hike_start: str = "") -> str:
    """Run the planner graph and return the output text. Used by API and CLI."""
    graph = get_graph()
    result = graph.invoke({
        "input": home_address.strip(),
        "arrival_day_time": hike_start.strip() if hike_start else "",
        "research": "",
        "output": "",
    })
    return result.get("output", "")


def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Set ANTHROPIC_API_KEY in .env to run this demo.")
        return
    try:
        get_graph()
    except ImportError:
        print("Install LangGraph: pip install langgraph")
        return
    except ValueError as e:
        print(e)
        return
    print("Hiking Trip Planner — Geocode → (Weather + Trails in parallel) → Planner (itinerary + social post)\n")
    print("Example: 123 Main St, Vancouver BC — then Saturday 9:00 AM.\n")
    while True:
        try:
            address = input("Home address (and any preferences): ").strip()
            if not address:
                continue
            arrival = input("Desired arrival at trail (e.g. Saturday 9:00 AM) [optional]: ").strip()
            output = run_plan(address, arrival)
            print("\n" + "=" * 60)
            print(output)
            print("=" * 60 + "\n")
        except KeyboardInterrupt:
            print("\nBye.")
            break


if __name__ == "__main__":
    main()
