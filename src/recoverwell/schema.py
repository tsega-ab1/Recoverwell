"""Input context for one recommendation request."""
from dataclasses import dataclass, field


@dataclass
class Context:
    user_id: str
    mood: float            # 1..5 daily assessment
    energy: float          # 1..5
    stress: float          # 1..5
    sleep_hours: float     # wearable
    hrv_ms: float | None   # wearable; None if unavailable
    steps_so_far: int      # wearable
    free_minutes: int      # calendar: minutes until next event
    meetings_today: int    # calendar
    hour: int              # local hour 0..23
    prefs: dict[str, float] = field(default_factory=dict)  # category -> 0..1
    outdoor_ok: bool = True
