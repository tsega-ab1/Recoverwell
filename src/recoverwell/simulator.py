"""Synthetic workplace-wellbeing world.

Ground truth is hidden from every policy: users have latent category affinities
(reported `prefs` are a noisy view of them), and completion probability depends
on context-activity interactions. Replace with real logged data when available.
"""
import math

import numpy as np

from .catalog import CATEGORIES, Activity
from .schema import Context


def _sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


class World:
    def __init__(self, n_users: int = 50, seed: int = 0):
        self.rng = np.random.default_rng(seed)
        self.affinity = self.rng.beta(2, 2, size=(n_users, len(CATEGORIES)))
        self.n_users = n_users

    def sample_context(self) -> Context:
        r = self.rng
        u = int(r.integers(self.n_users))
        stress = float(np.clip(r.normal(3.0, 1.0), 1, 5))
        energy = float(np.clip(r.normal(3.2 - 0.3 * (stress - 3), 0.9), 1, 5))
        mood = float(np.clip(r.normal(3.3 - 0.4 * (stress - 3), 0.8), 1, 5))
        prefs = np.clip(self.affinity[u] + r.normal(0, 0.15, len(CATEGORIES)), 0, 1)
        return Context(
            user_id=f"u{u}", mood=mood, energy=energy, stress=stress,
            sleep_hours=float(np.clip(r.normal(6.8, 1.1), 3.5, 9.5)),
            hrv_ms=None if r.random() < 0.2 else float(np.clip(r.normal(50, 15), 10, 110)),
            steps_so_far=int(r.integers(500, 9000)),
            free_minutes=int(r.choice([3, 5, 10, 15, 20, 30])),
            meetings_today=int(min(r.poisson(4), 10)),
            hour=int(r.integers(9, 18)),
            prefs={c: float(p) for c, p in zip(CATEGORIES, prefs)},
        )

    def true_prob(self, ctx: Context, a: Activity) -> float:
        u = int(ctx.user_id[1:])
        aff = self.affinity[u][CATEGORIES.index(a.category)]
        stress_z, energy_z = (ctx.stress - 3) / 2, (ctx.energy - 3) / 2
        sleep_def = max(0.0, (7 - ctx.sleep_hours) / 2)
        z = -0.2 + 2.0 * (aff - 0.5)
        if a.category in ("breathing", "mindfulness"):
            z += 0.9 * stress_z
        z += 1.2 * energy_z * a.intensity - 1.0 * sleep_def * a.intensity
        if a.outdoors:
            z += 0.5 if 10 <= ctx.hour <= 16 else -0.5
        if a.category == "social":
            z -= 0.4 * (ctx.meetings_today - 4) / 4
        z -= 0.04 * (a.duration_min - 10)
        return _sigmoid(z)

    def feedback(self, ctx: Context, a: Activity) -> float:
        return float(self.rng.random() < self.true_prob(ctx, a))
