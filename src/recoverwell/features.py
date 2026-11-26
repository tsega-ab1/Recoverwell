"""Feature extraction: Context -> fixed-length numeric vector."""
import math

import numpy as np

from .catalog import CATEGORIES
from .schema import Context

FEATURE_NAMES = (
    ["bias", "mood", "energy", "stress", "sleep", "hrv", "hrv_missing",
     "steps", "meetings", "hour_sin", "hour_cos"]
    + [f"pref_{c}" for c in CATEGORIES]
)
DIM = len(FEATURE_NAMES)


def _clip(v: float, lo: float = -2.0, hi: float = 2.0) -> float:
    return max(lo, min(hi, v))


def to_vector(ctx: Context) -> np.ndarray:
    hrv_missing = ctx.hrv_ms is None
    hrv = 0.0 if hrv_missing else _clip((ctx.hrv_ms - 50.0) / 25.0)
    ang = 2 * math.pi * ctx.hour / 24.0
    x = [
        1.0,
        (ctx.mood - 3) / 2,
        (ctx.energy - 3) / 2,
        (ctx.stress - 3) / 2,
        _clip((ctx.sleep_hours - 7.0) / 2.0),
        hrv,
        1.0 if hrv_missing else 0.0,
        _clip(ctx.steps_so_far / 8000.0, 0, 2),
        _clip((ctx.meetings_today - 4) / 4.0),
        math.sin(ang),
        math.cos(ang),
    ] + [ctx.prefs.get(c, 0.5) - 0.5 for c in CATEGORIES]
    return np.asarray(x, dtype=float)
