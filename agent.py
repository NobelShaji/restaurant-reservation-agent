# agent.py
"""
Very simple restaurant 'agent' that can:
- Receive a user message
- Decide which tool to call (for now: always search_restaurants)
- Call the tool and return structured results

Later, you can plug in a real LLM to decide tool + arguments.
"""

from dataclasses import asdict
from typing import Any, Dict, List

from tools import tool_search_restaurants
from restaurant_core import Restaurant


class RestaurantAgent:
    """
    A minimal agent wrapper.

    For now:
    - decide_tool_and_args is rule-based and ignores most of the user message.
    - In the future, you can replace that with an LLM call to parse the text
      into structured arguments.
    """

    def __init__(self, llm_client: Any = None):
        self.llm_client = llm_client

    def decide_tool_and_args(self, user_message: str) -> Dict[str, Any]:
        """
        Decide which tool to call and with what arguments.

        Right now this is a placeholder:
        - Always calls search_restaurants
        - Uses some simple defaults

        Later:
        - Parse city, cuisine, time, budget, etc. from user_message
          using an LLM or better NLP.
        """

        # Very naive defaults just so the agent works
        # You can improve this later.
        args: Dict[str, Any] = {
            "city": "Richmond",
            "neighborhood": None,
            "cuisine": None,
            "people": 2,
            "time_range_start": "18:00",
            "time_range_end": "21:00",
            "max_budget_per_person": None,
        }

        # Simple keyword-based tweaks (just to feel a bit smarter)
        lower_msg = user_message.lower()

        if "indian" in lower_msg:
            args["cuisine"] = "Indian"
        if "short pump" in lower_msg:
            args["neighborhood"] = "Short Pump"
        if "cheap" in lower_msg or "budget" in lower_msg:
            args["max_budget_per_person"] = 30.0
        if "two of us" in lower_msg or "2 of us" in lower_msg:
            args["people"] = 2
        if "four of us" in lower_msg or "4 of us" in lower_msg:
            args["people"] = 4

        return {
            "tool_name": "search_restaurants",
            "args": args,
        }

    def handle_message(self, user_message: str) -> Dict[str, Any]:
        """
        Main entrypoint for the agent.

        - Runs planning (decide_tool_and_args)
        - Calls the chosen tool
        - Returns JSON-serializable dict
        """
        decision = self.decide_tool_and_args(user_message)
        tool_name = decision.get("tool_name")
        args = decision.get("args", {})

        if tool_name == "search_restaurants":
            candidates: List[Restaurant] = tool_search_restaurants(**args)

            return {
                "tool_used": tool_name,
                "tool_args": args,
                "candidates": [asdict(c) for c in candidates],
            }

        # Fallback if we ever add more tools and get an unknown name
        return {
            "tool_used": None,
            "tool_args": args,
            "candidates": [],
            "error": f"Unknown tool '{tool_name}'",
        }

