"""Minimal service: POST /recommend, POST /feedback. In-memory model (v0)."""
from fastapi import FastAPI
from pydantic import BaseModel

from .catalog import BY_ID
from .policies import HybridPolicy
from .safety import SUPPORT_MESSAGE, needs_support_prompt
from .schema import Context

app = FastAPI(title="recoverwell", version="0.1.0")
policy = HybridPolicy()
_pending: dict[str, Context] = {}  # request_id -> context awaiting feedback


class ContextIn(BaseModel):
    request_id: str
    user_id: str
    mood: float
    energy: float
    stress: float
    sleep_hours: float
    hrv_ms: float | None = None
    steps_so_far: int = 0
    free_minutes: int
    meetings_today: int = 0
    hour: int
    prefs: dict[str, float] = {}
    outdoor_ok: bool = True


class FeedbackIn(BaseModel):
    request_id: str
    activity_id: str
    completed: bool


@app.get("/health")
def health():
    return {"status": "ok", "blend_lambda": round(policy.lam, 3)}


@app.post("/recommend")
def recommend(body: ContextIn):
    data = body.model_dump()
    rid = data.pop("request_id")
    ctx = Context(**data)
    _pending[rid] = ctx
    act, why = policy.recommend(ctx)
    return {
        "activity_id": act.id, "category": act.category,
        "duration_min": act.duration_min, "reasons": why,
        "support_message": SUPPORT_MESSAGE if needs_support_prompt(ctx) else None,
    }


@app.post("/feedback")
def feedback(body: FeedbackIn):
    ctx = _pending.pop(body.request_id, None)
    if ctx is None or body.activity_id not in BY_ID:
        return {"updated": False}
    policy.update(ctx, BY_ID[body.activity_id], 1.0 if body.completed else 0.0)
    return {"updated": True}
