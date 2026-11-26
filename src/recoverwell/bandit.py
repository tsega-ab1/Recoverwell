"""Disjoint LinUCB contextual bandit with Sherman-Morrison inverse updates."""
import numpy as np


class LinUCB:
    def __init__(self, arms: list[str], dim: int, alpha: float = 0.5, l2: float = 1.0):
        self.alpha = alpha
        self.Ainv = {a: np.eye(dim) / l2 for a in arms}
        self.b = {a: np.zeros(dim) for a in arms}
        self.n = {a: 0 for a in arms}

    def predict(self, arm: str, x: np.ndarray) -> tuple[float, float]:
        Ai = self.Ainv[arm]
        theta = Ai @ self.b[arm]
        return float(theta @ x), float(self.alpha * np.sqrt(max(x @ Ai @ x, 0.0)))

    def update(self, arm: str, x: np.ndarray, reward: float) -> None:
        Ai = self.Ainv[arm]
        Ax = Ai @ x
        self.Ainv[arm] = Ai - np.outer(Ax, Ax) / (1.0 + x @ Ax)
        self.b[arm] = self.b[arm] + reward * x
        self.n[arm] += 1

    @property
    def total_updates(self) -> int:
        return sum(self.n.values())
