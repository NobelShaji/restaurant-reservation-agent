# tools.py
"""
Tool layer for the restaurant agent.

This wraps core functions from restaurant_core.py into
agent-friendly "tools" that can be called with structured args.
"""

from typing import List, Optional

from restaurant_core import search_restaurants, Restaurant, load_restaurants

# Load restaurants once at startup and reuse
RESTAURANTS: List[Restaurant] = load_restaurants("restaurants.csv")


def tool_search_restaurants(
    city: str,
    neighborhood: Optional[str] = None,
    cuisine: Optional[str] = None,
    people: int = 2,
    time_range_start: str = "18:00",
    time_range_end: str = "21:00",
    max_budget_per_person: Optional[float] = None,
) -> List[Restaurant]:
    """
    Agent-facing wrapper around search_restaurants.

    Parameters
    ----------
    city : str
        City to search in (e.g., "Richmond").
    neighborhood : Optional[str]
        Neighborhood filter (e.g., "Short Pump"), or None for any.
    cuisine : Optional[str]
        Cuisine filter (e.g., "Indian"), or None for any.
    people : int
        Number of people in the party.
    time_range_start : str
        Earliest acceptable time in HH:MM (24h) format.
    time_range_end : str
        Latest acceptable time in HH:MM (24h) format.
    max_budget_per_person : Optional[float]
        Maximum budget per person, or None for no limit.

    Returns
    -------
    List[Restaurant]
        Matching restaurant candidates.
    """
    return search_restaurants(
        restaurants=RESTAURANTS,
        city=city,
        neighborhood=neighborhood,
        cuisine=cuisine,
        people=people,
        time_range_start=time_range_start,
        time_range_end=time_range_end,
        max_budget_per_person=max_budget_per_person,
    )

