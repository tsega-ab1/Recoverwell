"""Offline evaluation in the simulator: reward, regret vs oracle, learning curve."""
import numpy as np

from .policies import BanditPolicy, HybridPolicy, Policy, RandomPolicy, RulePolicy
from .safety import eligible
from .simulator import World


def run(policy: Policy, rounds: int, n_users: int, seed: int, window: int = 500) -> dict:
    world = World(n_users=n_users, seed=seed)  # identical world/context stream per policy
    p_chosen, p_best, rewards = [], [], []
    for _ in range(rounds):
        ctx = world.sample_context()
        act, _why = policy.recommend(ctx)
        r = world.feedback(ctx, act)
        policy.update(ctx, act, r)
        p_chosen.append(world.true_prob(ctx, act))
        p_best.append(max(world.true_prob(ctx, a) for a in eligible(ctx)))
        rewards.append(r)
    p_chosen, p_best = np.array(p_chosen), np.array(p_best)
    wins = [round(float(p_chosen[i:i + window].mean()), 4) for i in range(0, rounds, window)]
    return {
        "policy": policy.name,
        "completion_rate": round(float(np.mean(rewards)), 4),
        "mean_expected_completion": round(float(p_chosen.mean()), 4),
        "oracle_expected_completion": round(float(p_best.mean()), 4),
        "cumulative_regret": round(float((p_best - p_chosen).sum()), 1),
        "learning_curve": wins,
    }


def compare(rounds: int = 6000, n_users: int = 50, seed: int = 0) -> list[dict]:
    makers = [RandomPolicy, RulePolicy, BanditPolicy, HybridPolicy]
    return [run(m(), rounds, n_users, seed) for m in makers]
