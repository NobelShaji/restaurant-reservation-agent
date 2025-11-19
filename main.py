from restaurant_core import (
    load_restaurants,
    search_restaurants,
    Restaurant,
)

def main():
    print("Restaurant search demo (interactive)\n")

    restaurants = load_restaurants()

    # --- Ask user for inputs (structured for now) ---
    city = input("City (default: Richmond): ").strip() or "Richmond"
    neighborhood = input("Neighborhood (optional, e.g. 'Short Pump'): ").strip() or None
    cuisine = input("Cuisine (optional, e.g. 'Indian', 'Italian'): ").strip() or None

    people_str = input("Number of people (default: 2): ").strip() or "2"
    try:
        people = int(people_str)
    except ValueError:
        print("Invalid number, using 2.")
        people = 2

    time_start = input("Earliest time (HH:MM, default: 19:00): ").strip() or "19:00"
    time_end = input("Latest time (HH:MM, default: 21:00): ").strip() or "21:00"

    budget_str = input("Max budget per person (optional, e.g. 30): ").strip()
    max_budget = float(budget_str) if budget_str else None

    query = {
        "city": city,
        "neighborhood": neighborhood,
        "cuisine": cuisine,
        "people": people,
        "time_range_start": time_start,
        "time_range_end": time_end,
        "max_budget_per_person": max_budget,
    }

    print("\nSearching with:")
    print(query)
    print()

    matches = search_restaurants(restaurants, **query)

    if not matches:
        print("No matching restaurants found.")
        return

    print(f"Found {len(matches)} matching restaurant(s). Top results:\n")
    for r in matches:
        slots_str = ", ".join(s.strftime("%H:%M") for s in r.available_slots)
        print(
            f"- {r.name} ({r.neighborhood}) - {r.cuisine}, "
            f"${r.avg_price_per_person} per person, rating {r.rating}, "
            f"slots: {slots_str}"
        )
