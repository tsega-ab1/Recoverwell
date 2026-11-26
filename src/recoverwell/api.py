"""FastAPI service for contextual recovery recommendations.

The v0 policy and pending feedback are process-local. Use a persistent store
before running multiple instances or collecting real user data.
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .catalog import BY_ID
from .policies import HybridPolicy
from .safety import SUPPORT_MESSAGE, needs_support_prompt
from .schema import Context

app = FastAPI(title="Recoverwell API", version="0.2.0")

_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,https://tsega-ab1.github.io",
    ).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

policy = HybridPolicy()
_pending: dict[str, Context] = {}


class ContextIn(BaseModel):
    request_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=128)
    mood: float = Field(ge=1, le=5)
    energy: float = Field(ge=1, le=5)
    stress: float = Field(ge=1, le=5)
    sleep_hours: float = Field(ge=0, le=24)
    hrv_ms: float | None = Field(default=None, ge=0, le=300)
    steps_so_far: int = Field(default=0, ge=0, le=100000)
    free_minutes: int = Field(ge=1, le=1440)
    meetings_today: int = Field(default=0, ge=0, le=50)
    hour: int = Field(ge=0, le=23)
    prefs: dict[str, float] = Field(default_factory=dict)
    outdoor_ok: bool = True


class FeedbackIn(BaseModel):
    request_id: str = Field(min_length=1, max_length=128)
    activity_id: str = Field(min_length=1, max_length=128)
    completed: bool


@app.get("/")
def root():
    return {"service": "Recoverwell API", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "policy": policy.name,
        "blend_lambda": round(policy.lam, 3),
        "pending_feedback": len(_pending),
    }


@app.post("/recommend")
def recommend(body: ContextIn):
    data = body.model_dump()
    request_id = data.pop("request_id")
    context = Context(**data)
    activity, reasons = policy.recommend(context)
    _pending[request_id] = context
    return {
        "request_id": request_id,
        "activity_id": activity.id,
        "category": activity.category,
        "duration_min": activity.duration_min,
        "reasons": reasons,
        "support_message": (
            SUPPORT_MESSAGE if needs_support_prompt(context) else None
        ),
    }


@app.post("/feedback")
def feedback(body: FeedbackIn):
    context = _pending.pop(body.request_id, None)
    if context is None or body.activity_id not in BY_ID:
        return {"updated": False, "reason": "unknown_request_or_activity"}

    policy.update(
        context,
        BY_ID[body.activity_id],
        1.0 if body.completed else 0.0,
    )
    return {"updated": True, "blend_lambda": round(policy.lam, 3)}
