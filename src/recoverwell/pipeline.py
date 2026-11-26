"""CLI: python -m recoverwell.pipeline --rounds 6000 --out reports/metrics.json"""
import argparse
import json
from pathlib import Path

from .evaluate import compare


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=6000)
    ap.add_argument("--users", type=int, default=50)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="reports/metrics.json")
    args = ap.parse_args()

    res = compare(args.rounds, args.users, args.seed)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=2))

    print(f"{'policy':<10}{'completion':>12}{'expected':>10}{'oracle':>8}{'regret':>10}")
    for r in res:
        print(f"{r['policy']:<10}{r['completion_rate']:>12}{r['mean_expected_completion']:>10}"
              f"{r['oracle_expected_completion']:>8}{r['cumulative_regret']:>10}")


if __name__ == "__main__":
    main()
