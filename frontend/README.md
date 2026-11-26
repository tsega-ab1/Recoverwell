# Recoverwell Web

Next.js static-export frontend for the Recoverwell contextual recovery recommender.

## Local development

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

Without `NEXT_PUBLIC_API_URL`, the interface runs in clearly labelled demo mode. Set it to a deployed FastAPI origin to use live recommendations and feedback:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## GitHub Pages

The workflow in `.github/workflows/deploy-pages.yml` builds the static export and deploys it to GitHub Pages. Enable **Settings → Pages → Build and deployment → GitHub Actions** in the repository.

Set the repository Actions variable `NEXT_PUBLIC_API_URL` to the public backend URL to enable live API calls. This value is public by design; never put secrets in a `NEXT_PUBLIC_*` variable.

The production site path is `/Recoverwell/`.
