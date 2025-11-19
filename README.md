# Restaurant Reservation Agent (AI-ready Prototype)

## Overview

This project is a **restaurant reservation assistant API** that can:

- Accept **natural language** queries like  
  > "Find me an Indian restaurant in Short Pump in Richmond at 8pm for 4 people under 30 dollars"
- Convert them into **structured search filters** (city, neighborhood, cuisine, people, time window, budget).
- Use a **Python search tool** over a small CSV restaurant dataset.
- Return both:
  - A friendly **text reply**, and  
  - A structured list of matching restaurants (JSON).

It is designed to be an **agentic backend** that can later be plugged into:
- Azure AI Foundry / Prompt Flow,
- Other LLM-based agents (Gemini, GPT, etc.),
- Or a frontend / chatbot UI.

---

## Tech Stack

- **Language:** Python 3
- **Framework:** FastAPI
- **Server:** Uvicorn
- **Data:** `restaurants.csv` (mock restaurant database)
- **Architecture:**
  - Core search logic in `restaurant_core.py`
  - CLI demo in `main.py`
  - API + chat endpoints in `app.py`

---

## Files

- `restaurant_core.py`  
  Core logic:
  - `Restaurant` dataclass  
  - `load_restaurants()` – loads data from `restaurants.csv`  
  - `search_restaurants()` – filters and ranks restaurants

- `restaurants.csv`  
  Sample restaurant data (name, city, neighborhood, cuisine, price, rating, hours, time slots).

- `main.py`  
  Interactive CLI demo where you type structured inputs (city, cuisine, time, budget) and see results in the terminal.

- `app.py`  
  FastAPI app with:
  - `GET /` – health check  
  - `POST /search_restaurants` – structured search API  
  - `POST /chat` – natural language agent endpoint

---

## How to Run

### 1. Install dependencies

From the project folder:

```bash
pip install fastapi uvicorn pydantic
(If you already installed them earlier, you can skip this.)

2. Run the API server
bash
Copy code
cd /Users/nobel/Desktop/restaurant_agent
uvicorn app:app --reload
You should see:

text
Copy code
Uvicorn running on http://127.0.0.1:8000
3. Test via browser (Swagger UI)
Open:

http://127.0.0.1:8000/ → health check

http://127.0.0.1:8000/docs → auto-generated API docs

Example: structured search
Use POST /search_restaurants with:

json
Copy code
{
  "city": "Richmond",
  "neighborhood": "Short Pump",
  "cuisine": "Indian",
  "people": 4,
  "time_range_start": "19:00",
  "time_range_end": "21:00",
  "max_budget_per_person": 30
}
Example: chat-style request
Use POST /chat with:

json
Copy code
{
  "message": "Find me an Indian restaurant in Short Pump in Richmond at 8pm for 4 people under 30 dollars"
}
You’ll get a response like:

A natural language reply listing 1–3 options.

A candidates array with full restaurant details and available time slots.

Future Work / Azure AI Design
This project is intentionally built to map cleanly into Azure AI Foundry (or other LLM platforms):

Node 1 – LLM Parser
Replace the rule-based parse_message_to_search() with an LLM that outputs JSON:

json
Copy code
{
  "city": "...",
  "neighborhood": "...",
  "cuisine": "...",
  "people": 4,
  "time_range_start": "19:00",
  "time_range_end": "21:00",
  "max_budget_per_person": 30
}
Node 2 – Python Tool
Use search_restaurants() as a tool node that searches restaurants.csv or an indexed data store.

Node 3 – LLM Responder
Use an LLM node to turn the candidates into a rich conversational answer and ask for confirmation.

This design also generalizes to:

Airline reservation agents,

Hotel booking,

Event ticketing,

And other agentic decision-support systems.
