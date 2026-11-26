"""Hard constraints applied BEFORE any model ranks anything.

Models only ever choose among activities that pass `eligible`. Safety is not
learned; it is enforced.
"""
from .catalog import CATALOG, Activity
from .schema import Context

SUPPORT_MESSAGE = (
    "Your check-in suggests a hard moment. Consider reaching out to someone you "
    "trust or your organisation's support resources."
)


def needs_support_prompt(ctx: Context) -> bool:
    return ctx.mood <= 1.5 and ctx.stress >= 4.5


def intensity_cap(ctx: Context) -> float:
    cap = 1.0
    if ctx.sleep_hours < 5.0:
        cap = min(cap, 0.5)
    if ctx.hrv_ms is not None and ctx.hrv_ms < 25.0:
        cap = min(cap, 0.5)
    if ctx.energy <= 1.5:
        cap = min(cap, 0.3)
    return cap


def eligible(ctx: Context, catalog: list[Activity] = CATALOG) -> list[Activity]:
    cap = intensity_cap(ctx)
    out = [
        a for a in catalog
        if a.duration_min <= ctx.free_minutes
        and a.intensity <= cap
        and (ctx.outdoor_ok or not a.outdoors)
    ]
    if not out:  # always have a fallback: shortest zero-intensity activity
        out = [min((a for a in catalog if a.intensity == 0.0), key=lambda a: a.duration_min)]
    return out
