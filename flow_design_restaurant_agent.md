# Restaurant Reservation Agent – Flow Design

## Inputs
- user_query (free text from user, e.g. "find me an Indian restaurant in Short Pump...")

## Node 1 – LLM Parser (Foundry)
Goal: Convert user_query into structured JSON.

Output JSON shape:
{
  "city": "Richmond",
  "neighborhood": "Short Pump",
  "date": "2025-03-15",
  "time_range_start": "19:00",
  "time_range_end": "21:00",
  "people": 4,
  "cuisine": "Indian",
  "max_budget_per_person": 30.0
}

## Node 2 – Python Tool: search_restaurants
Input: the JSON above, mapped to function arguments:
- city
- neighborhood
- cuisine
- people
- time_range_start
- time_range_end
- max_budget_per_person

Output: list of Restaurant candidates (name, neighborhood, cuisine, price, rating, slots).

## Node 3 – LLM Responder
Input:
- user_query
- parsed_request JSON
- candidates (from Node 2)

Output: natural language answer listing 2–3 best options and asking for confirmation.

"""
In Azure AI Foundry Prompt Flow, we’ll replace the structured input step with:

A chat LLM node that:

Takes messy user text like:

“Find me an Indian restaurant in Short Pump tonight around 8 for 4 people under $30.”

Outputs the JSON:

{ "city": "Richmond", "neighborhood": "Short Pump", "people": 4, ... }


…and then call the exact same logic you just built as a Python tool node.
"""
