"""Activity catalog. Intensity is 0 (rest) .. 1 (hard exertion)."""
from dataclasses import dataclass

CATEGORIES = ["breathing", "movement", "mindfulness", "social", "nature", "creative"]


@dataclass(frozen=True)
class Activity:
    id: str
    category: str
    duration_min: int
    intensity: float
    outdoors: bool = False


CATALOG = [
    Activity("box_breathing_3", "breathing", 3, 0.0),
    Activity("breathing_478_5", "breathing", 5, 0.0),
    Activity("desk_stretch_5", "movement", 5, 0.2),
    Activity("walk_10", "movement", 10, 0.4, True),
    Activity("brisk_walk_20", "movement", 20, 0.7, True),
    Activity("hiit_15", "movement", 15, 1.0),
    Activity("body_scan_10", "mindfulness", 10, 0.0),
    Activity("guided_meditation_15", "mindfulness", 15, 0.0),
    Activity("call_a_friend_10", "social", 10, 0.1),
    Activity("coffee_with_colleague_15", "social", 15, 0.1),
    Activity("green_break_10", "nature", 10, 0.2, True),
    Activity("sketch_10", "creative", 10, 0.1),
    Activity("music_break_5", "creative", 5, 0.0),
]
BY_ID = {a.id: a for a in CATALOG}
