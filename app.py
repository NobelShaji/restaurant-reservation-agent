from dataclasses import asdict
from typing import List, Optional, Any

from fastapi import FastAPI
from pydantic import BaseModel

from restaurant_core import Restaurant, search_restaurants, load_restaurants
from agent import RestaurantAgent

# Create FastAPI app
app = FastAPI(title="Restaurant Reservation Agent API")

# Load restaurants once for the direct search endpoint
RESTAURANTS: List[Restaurant] = load_restaurants("restaurants.csv")

# Create a single agent instance for the app
agent = RestaurantAgent(llm_client=None)


# ---------- Pydantic models ----------

class RestaurantSearchRequest(BaseModel):
    city: str
    neighborhood: Optional[str] = None
    cuisine: Optional[str] = None
    people: int = 2
    time_range_start: str = "18:00"
    time_range_end: str = "21:00"
    max_budget_per_person: Optional[float] = None


class ChatRequest(BaseModel):
    message: str


class RestaurantResponse(BaseModel):
    name: str
    city: str
    neighborhood: str
    cuisine: str
    avg_price_per_person: float
    rating: float
    available_slots: List[str]


# ---------- Basic health endpoint ----------

@app.get("/")
def root():
    return {"message": "Restaurant agent API is running. Go to /docs for Swagger UI."}


# ---------- Direct search endpoint (tool-style) ----------

@app.post("/search_restaurants")
def search_restaurants_endpoint(req: RestaurantSearchRequest):
    """
    Direct, structured search endpoint that calls search_restaurants()
    without going through the agent.
    """
    candidates: List[Restaurant] = search_restaurants(
        restaurants=RESTAURANTS,
        city=req.city,
        neighborhood=req.neighborhood,
        cuisine=req.cuisine,
        people=req.people,
        time_range_start=req.time_range_start,
        time_range_end=req.time_range_end,
        max_budget_per_person=req.max_budget_per_person,
    )

    return {
        "candidates": [asdict(c) for c in candidates],
    }


# ---------- Agent raw endpoint ----------

@app.post("/agent_chat")
def agent_chat(req: ChatRequest):
    """
    Low-level agent endpoint.

    - Takes a free-form message
    - Runs it through RestaurantAgent.handle_message
    - Returns tool_used, tool_args, and candidates as-is
    """
    result = agent.handle_message(req.message)
    return result


# ---------- Agent + friendly reply endpoint ----------

@app.post("/chat")
def chat(req: ChatRequest):
    """
    Higher-level chat endpoint.

    - Uses the agent to get candidates
    - Builds a human-friendly reply summarizing the best option(s)
    """
    result = agent.handle_message(req.message)
    candidates = result.get("candidates", [])

    if not candidates:
        reply = "I couldn't find any restaurants matching your request."
        return {
            "reply": reply,
            "candidates": candidates,
            "debug": {
                "tool_used": result.get("tool_used"),
                "tool_args": result.get("tool_args"),
            },
        }

    # Take the first candidate as the main suggestion
    first: dict[str, Any] = candidates[0]
    name = first.get("name")
    city = first.get("city")
    neighborhood = first.get("neighborhood") or ""
    cuisine = first.get("cuisine") or ""
    price = first.get("avg_price_per_person")
    rating = first.get("rating")
    slots = first.get("available_slots", [])

    # Convert any datetime.time objects to "HH:MM" strings
    display_slots: List[str] = []
    for s in slots[:3]:
        if isinstance(s, str):
            display_slots.append(s)
        else:
            try:
                display_slots.append(s.strftime("%H:%M"))
            except AttributeError:
                display_slots.append(str(s))

    slots_str = ", ".join(display_slots)

    reply = (
        f"Here is a good option: {name} in "
        f"{neighborhood or city} "
        f"({cuisine}, around ${price} per person, rating {rating})."
    )
    if slots_str:
        reply += f" Available times include: {slots_str}."

    if len(candidates) > 1:
        reply += f" I also found {len(candidates) - 1} more option(s) you can review in the response."

    return {
        "reply": reply,
        "candidates": candidates,
        "debug": {
            "tool_used": result.get("tool_used"),
            "tool_args": result.get("tool_args"),
        },
    }

