# Recoverwell

**Context-aware recovery activity recommendations, built to be explainable first and adaptive over time.**

Recoverwell explores how daily check-ins, schedule context, wearable signals and personal preferences can help recommend small recovery activities at appropriate moments.

> Research prototype. It is not a medical device, does not diagnose or treat conditions, and its illustrative safety thresholds and synthetic evaluation results are not clinically validated.

## Product

The repository contains two connected parts:

- **Python recommendation engine** — safety eligibility, explainable rule scoring, LinUCB contextual bandit, hybrid policy, synthetic simulation and FastAPI.
- **Next.js web experience** — responsive wellbeing check-in, live recommendation and feedback flow, model strategy overview and illustrative analytics.

## Architecture

```text
Next.js web app (GitHub Pages)
        |  check-in / feedback
        v
FastAPI service (Render or another Python host)
        |
        v
Recoverwell recommendation engine
  1. Safety eligibility filter (hard constraints)
  2. Explainable rule-based baseline
  3. LinUCB residual learner
  4. Ranked activity + human-readable reasons
        |
        v
Feedback updates the contextual policy
```

The safety filter is applied before ranking. The model cannot learn to bypass its eligibility constraints.

## Run locally

### Python API

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src uvicorn recoverwell.api:app --reload
```

API docs: http://localhost:8000/docs

### Web application

In a second terminal:

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open http://localhost:3000.

If `NEXT_PUBLIC_API_URL` is not set, the web app runs in a clearly labelled local demo mode. Demo recommendations and feedback are not sent to or learned by the Python engine.

### Tests and simulation

```bash
PYTHONPATH=src pytest -q
PYTHONPATH=src python -m recoverwell.pipeline --rounds 20000 --out reports/metrics.json
```

## Deployment

### 1. Deploy the API

The included `render.yaml` describes a Render web service. Create a new Blueprint deployment from this repository. The API uses the `ALLOWED_ORIGINS` environment variable for browser CORS access.

The current v0 API keeps its policy state and pending feedback in process memory. It is suitable for a single-instance prototype, not durable production use. A restart loses learned state; multiple instances will not share it. Add persistent storage and user authentication before collecting real personal data.

### 2. Deploy the frontend to GitHub Pages

1. Open repository **Settings → Pages**.
2. Set **Build and deployment → Source** to **GitHub Actions**.
3. In **Settings → Secrets and variables → Actions → Variables**, add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: the deployed API origin, e.g. `https://your-service.onrender.com`
4. Push changes to `main` or `feature/full-stack-platform`, or run the **Deploy Recoverwell web** workflow manually.

The static site is exported from `frontend/out` and served at:

`https://tsega-ab1.github.io/Recoverwell/`

The frontend variable is public at build time. Never put API keys, credentials or private tokens in `NEXT_PUBLIC_*` variables.

## Recommendation API

### `POST /recommend`

Accepts a request ID, user context and optional preferences. Returns the selected activity, duration, explanation reasons and an optional support prompt.

### `POST /feedback`

Accepts the recommendation request ID, activity ID and completion outcome. The v0 process-local hybrid policy uses the outcome to update its LinUCB residual model.

### `GET /health`

Returns API health and the current hybrid learning blend.

## Current ML approach

- **Random** — reference baseline.
- **Rules** — explainable cold-start policy.
- **LinUCB** — contextual bandit.
- **Hybrid** — rules provide the prior; LinUCB learns a residual correction from feedback.

The current simulator is synthetic. Its results measure behavior inside the simulator, not real-world wellbeing improvement. The next evaluation milestone is to stress-test misspecified rules and compare policies over multiple seeds with uncertainty intervals.

## Roadmap

- [x] Explainable rule-based recommendations and hard safety eligibility.
- [x] LinUCB contextual bandit and hybrid policy.
- [x] Synthetic simulation and policy comparison.
- [x] FastAPI recommendation and feedback endpoints.
- [x] Interactive Next.js check-in and recommendation experience.
- [x] GitHub Pages deployment workflow and Render service blueprint.
- [ ] Persistent feedback and model state (database-backed).
- [ ] Reproducible multi-seed evaluation and confidence intervals.
- [ ] Off-policy evaluation (IPS / doubly robust).
- [ ] MLflow experiment tracking and model versioning.
- [ ] Consent, data minimization, retention and access controls.
- [ ] Scientific review of the activity catalogue, safety rules and outcome measures.

## Responsible-use principles

- Collect only the context needed for a recommendation.
- Treat wearable and wellbeing signals as sensitive personal data.
- Make recommendations explainable and easy to decline.
- Keep safety constraints outside the learning objective.
- Do not interpret activity completion as proof of improved health.
- Validate any wellbeing outcome claims with appropriate scientific review.
