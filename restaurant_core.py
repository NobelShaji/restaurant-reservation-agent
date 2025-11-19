from dataclasses import dataclass
from typing import List, Optional
import csv
from datetime import datetime, time


@dataclass
class Restaurant:
    name: str
    city: str
    neighborhood: str
    cuisine: str
    avg_price_per_person: float
    rating: float
    opens_at: time
    closes_at: time
    max_guests_per_slot: int
    available_slots: List[time]


def parse_time_str(s: str) -> time:
    return datetime.strptime(s.strip(), "%H:%M").time()


def load_restaurants(path: str = "restaurants.csv") -> List[Restaurant]:
    restaurants: List[Restaurant] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slots = [
                parse_time_str(t)
                for t in row["available_slots"].split(";")
                if t.strip()
            ]
            restaurants.append(
                Restaurant(
                    name=row["name"],
                    city=row["city"],
                    neighborhood=row["neighborhood"],
                    cuisine=row["cuisine"],
                    avg_price_per_person=float(row["avg_price_per_person"]),
                    rating=float(row["rating"]),
                    opens_at=parse_time_str(row["opens_at"]),
                    closes_at=parse_time_str(row["closes_at"]),
                    max_guests_per_slot=int(row["max_guests_per_slot"]),
                    available_slots=slots,
                )
            )
    return restaurants


def slot_in_range(slot: time, start: time, end: time) -> bool:
    # assume same day and start <= end
    return start <= slot <= end


def search_restaurants(
    restaurants: List[Restaurant],
    city: str,
    people: int,
    cuisine: Optional[str] = None,
    neighborhood: Optional[str] = None,
    time_range_start: Optional[str] = None,
    time_range_end: Optional[str] = None,
    max_budget_per_person: Optional[float] = None,
) -> List[Restaurant]:
    # parse time strings if provided
    start_t = parse_time_str(time_range_start) if time_range_start else None
    end_t = parse_time_str(time_range_end) if time_range_end else None

    results: List[Restaurant] = []

    for r in restaurants:
        # city must match
        if r.city.lower() != city.lower():
            continue

        # neighborhood filter (if provided)
        if neighborhood and r.neighborhood.lower() != neighborhood.lower():
            continue

        # cuisine filter (if provided)
        if cuisine and r.cuisine.lower() != cuisine.lower():
            continue

        # budget filter
        if max_budget_per_person is not None and r.avg_price_per_person > max_budget_per_person:
            continue

        # capacity filter
        if people > r.max_guests_per_slot:
            continue

        # time window filter (if provided)
        if start_t and end_t:
            has_slot = any(slot_in_range(s, start_t, end_t) for s in r.available_slots)
            if not has_slot:
                continue

        results.append(r)

    # sort by rating (desc), then price (asc)
    results.sort(key=lambda r: (-r.rating, r.avg_price_per_person))
    return results

