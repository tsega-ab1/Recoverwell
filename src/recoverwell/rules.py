"""Explainable rule-based recommender: the cold-start baseline.

Every score component is named, so every recommendation can say why.
Scores are roughly in [0, 1].
"""
from .catalog import Activity
from .schema import Context


def score(ctx: Context, a: Activity) -> tuple[float, list[str]]:
    s, why = 0.4, []
    pref = ctx.prefs.get(a.category, 0.5)
    s += 0.35 * (pref - 0.5)
    if pref >= 0.7:
        why.append(f"you tend to like {a.category} activities")

    if ctx.stress >= 3.5 and a.category in ("breathing", "mindfulness"):
        s += 0.25
        why.append("stress is high, so a calming activity fits")
    if ctx.energy >= 3.5 and a.category == "movement":
        s += 0.15
        why.append("you have energy to spend on movement")
    if ctx.energy <= 2.0 and a.intensity >= 0.5:
        s -= 0.25
        why.append("energy is low, so intense activities are down-weighted")
    if ctx.steps_so_far < 2500 and ctx.hour >= 11 and a.category == "movement":
        s += 0.1
        why.append("you've been fairly sedentary today")
    if a.outdoors and 10 <= ctx.hour <= 16:
        s += 0.08
        why.append("daylight hours suit an outdoor break")
    if a.category == "social" and ctx.meetings_today >= 6:
        s -= 0.15
        why.append("a heavy meeting day makes social breaks less appealing")
    if a.duration_min > 0.8 * ctx.free_minutes:
        s -= 0.05  # tight fit
    return max(0.0, min(1.0, s)), why
