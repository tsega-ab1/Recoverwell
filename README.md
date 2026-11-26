# recoverwell

Contextual recommendation of short recovery activities (breathing, movement, mindfulness, social, nature, creative) from daily check-ins, calendar load, wearable signals and stated preferences.

Design follows one principle: **start with explainable rules, then let feedback correct them.** v0 is general and runnable end to end; see Roadmap for what gets refined next.

## Architecture

```
Context (check-in + calendar + wearables + prefs)
   -> safety.eligible()     hard constraints: time window, intensity caps, outdoors; never learned
   -> rules.score()         explainable baseline, every score carries reasons
   -> LinUCB residual model learns (reward - rule_score) from completion feedback
   -> ranked activity + reasons  (+ support message when mood very low and stress very high)
```

| Module | Role |
|---|---|
| `schema.py`, `features.py` | context -> 17-dim feature vector (missing HRV handled explicitly) |
| `safety.py` | eligibility filter + support-prompt trigger |
| `rules.py` | cold-start baseline with explanations |
| `bandit.py` | disjoint LinUCB, Sherman-Morrison updates |
| `policies.py` | `random`, `rules`, `linucb`, `hybrid` behind one interface |
| `simulator.py`, `evaluate.py` | synthetic world, regret vs oracle, learning curves |
| `api.py` | FastAPI `/recommend` and `/feedback` |

## Run

```bash
pip install -r requirements.txt
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m recoverwell.pipeline --rounds 20000 --out reports/metrics.json
PYTHONPATH=src uvicorn recoverwell.api:app --reload      # or: docker build -t recoverwell . 
```

## Results (synthetic world, 20k rounds, 50 users, seed 0)

```
policy      completion  expected  oracle    regret
random          0.4819    0.4866  0.6231    2730.6
rules           0.5844    0.5869  0.6231     725.5
linucb          0.5752    0.5762  0.6231     939.5
hybrid          0.5857    0.5864  0.6231     735.9
```

`completion` = observed completion rate; `expected` = mean true completion probability of chosen activities; `oracle` = best eligible choice; `regret` = cumulative gap to oracle.

**Read this honestly.** In this simulator the hand-written rules already encode most of the true structure (I wrote both), so they are a strong baseline. The pure bandit is still improving at 20k rounds, and the hybrid roughly matches the rules. Learning pays off when the rules are *wrong* or users diverge from the population, which this v0 simulator does not yet stress. Real logged data is the real test.

## Roadmap (refinement order)

1. **Stress-test rule misspecification**: perturb the simulator so rules are miscalibrated; measure how fast the residual model recovers.
2. **Better models**: Thompson sampling, per-user random effects / hierarchical shrinkage, nonlinear features, then gradient-boosted reward model with bandit-style exploration.
3. **Off-policy evaluation**: log propensities; add IPS / doubly-robust estimators so new policies can be assessed on logged data before deployment.
4. **Metrics**: relevance (completion), timing (acceptance by time-of-day), engagement (retention), wellbeing delta from next check-in; define guardrail metrics.
5. **Pipeline / MLOps**: feature store, MLflow tracking, scheduled retraining (Airflow), model registry, drift monitoring, persistent model state.
6. **Safety and science**: advisor-reviewed activity catalog and rules, escalation policy, consent and privacy for wearable data.
7. **Companion integration**: expose ranked candidates + reasons to an LLM layer for natural-language explanation.

## Limitations

Synthetic data only; reward is completion, not validated wellbeing change; no persistence; the safety thresholds are illustrative, not clinically validated.
