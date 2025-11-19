from typing import List, Optional
import re

from fastapi import FastAPI
from pydantic import BaseModel

from restaurant_core import load_restaurants, search_restaurants, Restaurant


app = FastAPI(title="Restaurant Reservation Agent API")

# Load restaurant data once at startup
restaurants = load_restaurants()


class SearchRequest(BaseModel):
    city: str = "Richmond"
    neighborhood: Optional[str] = None
    cuisine: Optional[str] = None
    people: int = 2
    time_range_start: Optional[str] = "19:00"
    time_range_end: Optional[str] = "21:00"
    max_budget_per_person: Optional[float] = None


class RestaurantResponse(BaseModel):
    name: str
    city: str
    neighborhood: str
    cuisine: str
    avg_price_per_person: float
    rating: float
    available_slots: List[str]


class SearchResponse(BaseModel):
    candidates: List[RestaurantResponse]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    candidates: List[RestaurantResponse] = []


def parse_message_to_search(message: str) -> SearchRequest:
    """
    Very simple rule-based parser to turn a natural language message
    into a SearchRequest.
    """
    text = message.lower()

    # Defaults
    city = "Richmond"
    neighborhood: Optional[str] = None
    cuisine: Optional[str] = None
    people = 2
    time_range_start = "18:00"
    time_range_end = "21:00"
    max_budget_per_person: Optional[float] = None

    # City (only Richmond for now)
    if "richmond" in text:
        city = "Richmond"

    # Neighborhoods
    neighborhoods_map = {
        "short pump": "Short Pump",
        "downtown": "Downtown",
        "the fan": "The Fan",
    }
    for key, val in neighborhoods_map.items():
        if key in text:
            neighborhood = val
            break

    # Cuisines (based on our CSV)
    cuisines_list = ["indian", "italian", "vegetarian", "japanese"]
    for c in cuisines_list:
        if c in text:
            cuisine = c.capitalize()
            break

    # Number of people: look for "for 4", "for 2 people", etc.
    m = re.search(r"for\s+(\d+)", text)
    if m:
        try:
            people = int(m.group(1))
        except ValueError:
            pass

    # Budget: "under 30", "below 40", "max 25", etc.
    m = re.search(r"(under|below|max)\s*\$?\s*(\d+)", text)
    if m:
        try:
            max_budget_per_person = float(m.group(2))
        except ValueError:
            pass

    # Time: look for "at 8pm", "around 7 pm", etc.
    m = re.search(r"(\d{1,2})\s*(am|pm)", text)
    if m:
        hour = int(m.group(1))
        ampm = m.group(2)

        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0

        # 1-hour window around that time
        start_hour = max(0, hour - 1)
        end_hour = min(23, hour + 1)
        time_range_start = f"{start_hour:02d}:00"
        time_range_end = f"{end_hour:02d}:00"

    return SearchRequest(
        city=city,
        neighborhood=neighborhood,
        cuisine=cuisine,
        people=people,
        time_range_start=time_range_start,
        time_range_end=time_range_end,
        max_budget_per_person=max_budget_per_person,
    )


@app.get("/")
def root():
    return {"message": "Restaurant reservation agent API is running."}


@app.post("/search_restaurants", response_model=SearchResponse)
def search_restaurants_endpoint(req: SearchRequest):
    matches = search_restaurants(
        restaurants=restaurants,
        city=req.city,
        neighborhood=req.neighborhood,
        cuisine=req.cuisine,
        people=req.people,
        time_range_start=req.time_range_start,
        time_range_end=req.time_range_end,
        max_budget_per_person=req.max_budget_per_person,
    )

    result = [
        RestaurantResponse(
            name=r.name,
            city=r.city,
            neighborhood=r.neighborhood,
            cuisine=r.cuisine,
            avg_price_per_person=r.avg_price_per_person,
            rating=r.rating,
            available_slots=[s.strftime("%H:%M") for s in r.available_slots],
        )
        for r in matches
    ]

    return {"candidates": result}


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 1) Parse the natural language message into a SearchRequest
    search_req = parse_message_to_search(req.message)

    # 2) Run the same search logic
    matches = search_restaurants(
        restaurants=restaurants,
        city=search_req.city,
        neighborhood=search_req.neighborhood,
        cuisine=search_req.cuisine,
        people=search_req.people,
        time_range_start=search_req.time_range_start,
        time_range_end=search_req.time_range_end,
        max_budget_per_person=search_req.max_budget_per_person,
    )

    result = [
        RestaurantResponse(
            name=r.name,
            city=r.city,
            neighborhood=r.neighborhood,
            cuisine=r.cuisine,
            avg_price_per_person=r.avg_price_per_person,
            rating=r.rating,
            available_slots=[s.strftime("%H:%M") for s in r.available_slots],
        )
        for r in matches
    ]

    # 3) Generate a simple natural language reply
    if not result:
        reply = (
            "I couldn't find any matching restaurants for your request. "
            "Try changing the neighborhood, cuisine, time window, or budget."
        )
        return ChatResponse(reply=reply, candidates=[])

    lines = []
    lines.append("Here are some options I found:")

    for r in result[:3]:
        slots_str = ", ".join(r.available_slots[:3])
        lines.append(
            f"- {r.name} in {r.neighborhood} ({r.cuisine}, "
            f"~${r.avg_price_per_person} per person, rating {r.rating}), "
            f"available at: {slots_str}"
        )

    lines.append(
        "You can send another message if you want to change the cuisine, neighborhood, time or budget."
    )

    reply = "\n".join(lines)

    return ChatResponse(reply=reply, candidates=result)

