"""Recommendation policies behind one interface: recommend() / update()."""
import numpy as np

from . import rules
from .bandit import LinUCB
from .catalog import CATALOG, Activity
from .features import DIM, to_vector
from .safety import eligible
from .schema import Context


class Policy:
    name = "base"

    def recommend(self, ctx: Context) -> tuple[Activity, list[str]]:
        raise NotImplementedError

    def update(self, ctx: Context, activity: Activity, reward: float) -> None:
        pass


class RandomPolicy(Policy):
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = np.random.default_rng(seed)

    def recommend(self, ctx):
        el = eligible(ctx)
        return el[int(self.rng.integers(len(el)))], ["random baseline"]


class RulePolicy(Policy):
    name = "rules"

    def recommend(self, ctx):
        el = eligible(ctx)
        best = max(el, key=lambda a: rules.score(ctx, a)[0])
        return best, rules.score(ctx, best)[1]


class BanditPolicy(Policy):
    name = "linucb"

    def __init__(self, alpha: float = 0.5):
        self.model = LinUCB([a.id for a in CATALOG], DIM, alpha=alpha)

    def recommend(self, ctx):
        x = to_vector(ctx)
        best = max(eligible(ctx), key=lambda a: sum(self.model.predict(a.id, x)))
        return best, ["learned from feedback from similar contexts"]

    def update(self, ctx, activity, reward):
        self.model.update(activity.id, to_vector(ctx), reward)


class HybridPolicy(Policy):
    """Explainable rules as the prior; a LinUCB model learns the *residual*.

    final = rule_score + lam * (residual_mean + exploration_bonus)
    residual target = observed reward - rule_score, so with no data the policy
    IS the rule baseline, and feedback only ever corrects it.
    lam ramps 0 -> 1 over `warmup` updates.
    """
    name = "hybrid"

    def __init__(self, alpha: float = 0.1, warmup: int = 1000):
        self.model = LinUCB([a.id for a in CATALOG], DIM, alpha=alpha)
        self.warmup = warmup

    @property
    def lam(self) -> float:
        return min(1.0, self.model.total_updates / self.warmup)

    def recommend(self, ctx):
        x, lam = to_vector(ctx), self.lam

        def final(a: Activity) -> float:
            mean, bonus = self.model.predict(a.id, x)
            return rules.score(ctx, a)[0] + lam * (mean + bonus)

        best = max(eligible(ctx), key=final)
        why = rules.score(ctx, best)[1]
        if lam > 0.5:
            why = why + ["adjusted using feedback from similar contexts"]
        return best, why

    def update(self, ctx, activity, reward):
        resid = reward - rules.score(ctx, activity)[0]
        self.model.update(activity.id, to_vector(ctx), resid)
