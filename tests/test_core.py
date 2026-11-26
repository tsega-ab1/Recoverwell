import numpy as np

from recoverwell.bandit import LinUCB
from recoverwell.catalog import CATALOG
from recoverwell.evaluate import run
from recoverwell.features import DIM, to_vector
from recoverwell.policies import HybridPolicy, RandomPolicy
from recoverwell.rules import score
from recoverwell.safety import eligible, needs_support_prompt
from recoverwell.simulator import World


def ctx(**kw):
    c = World(5, 1).sample_context()
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def test_feature_vector_shape_and_missing_hrv():
    assert to_vector(ctx(hrv_ms=None)).shape == (DIM,)


def test_safety_caps_intensity_when_exhausted():
    c = ctx(sleep_hours=4.0, free_minutes=30, energy=1.0)
    assert all(a.intensity <= 0.3 for a in eligible(c))


def test_safety_respects_time_window_and_has_fallback():
    assert all(a.duration_min <= 5 for a in eligible(ctx(free_minutes=5)))
    assert len(eligible(ctx(free_minutes=1))) == 1


def test_support_prompt_trigger():
    assert needs_support_prompt(ctx(mood=1.0, stress=5.0))
    assert not needs_support_prompt(ctx(mood=3.0, stress=3.0))


def test_rules_explain_high_stress():
    c = ctx(stress=4.5, energy=3.0)
    breathing = next(a for a in CATALOG if a.category == "breathing")
    s, why = score(c, breathing)
    assert s > 0 and any("stress" in w for w in why)


def test_linucb_learns_best_arm():
    m = LinUCB(["a", "b"], dim=2, alpha=0.1)
    x = np.array([1.0, 0.0])
    for _ in range(100):
        m.update("a", x, 1.0)
        m.update("b", x, 0.0)
    assert m.predict("a", x)[0] > m.predict("b", x)[0]


def test_hybrid_beats_random_in_simulation():
    h = run(HybridPolicy(warmup=500), 3000, 30, seed=3)
    r = run(RandomPolicy(), 3000, 30, seed=3)
    assert h["mean_expected_completion"] > r["mean_expected_completion"]
