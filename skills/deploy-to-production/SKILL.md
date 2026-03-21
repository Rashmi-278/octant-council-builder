---
description: Export council output to a live Railway backend + Netlify dashboard with Ostrom radar charts and EAS attestation records
argument-hint: <slug>
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
model: sonnet
context: inherit
user-invocable: true
---

# Deploy Council to Production

Export the current council evaluation output to a live production app. This reads `council-out/$SLUG/` and deploys:
- **Railway**: 3 FastAPI services (collector, analyst, evaluator)
- **Netlify**: Next.js 15 dashboard with Ostrom radar charts, score breakdowns, and EAS attestation links

<progress>
- [ ] Step 1: Validate slug and council output
- [ ] Step 2: Check prerequisites
- [ ] Step 3: Stage data for deployment
- [ ] Step 4: Deploy backend
- [ ] Step 5: Deploy frontend
- [ ] Step 6: Print live URLs
</progress>

## Input

`$ARGUMENTS` is the slug of the council output to deploy (e.g., `protocol-guild`, `test-octant`).

If not provided, list available slugs from `council-out/` and ask the user to choose.

## Step 1: Validate Slug and Council Output

```bash
ls council-out/
```

Check that `council-out/$SLUG/` exists and has the expected subdirectories:
- `council-out/$SLUG/data/` — Wave 1 output (REQUIRED)
- `council-out/$SLUG/eval/` — Wave 2 output (expected)
- `council-out/$SLUG/synth/` — Wave 3 output (expected)

If the slug doesn't exist, show available slugs and ask the user to choose.

Show the user what data is available:

```bash
echo "=== Data files ===" && ls council-out/$SLUG/data/ 2>/dev/null || echo "(none)"
echo "=== Eval files ===" && ls council-out/$SLUG/eval/ 2>/dev/null || echo "(none)"
echo "=== Synth files ===" && ls council-out/$SLUG/synth/ 2>/dev/null || echo "(none)"
```

## Step 2: Check Prerequisites

```bash
command -v railway && echo "Railway CLI: OK" || echo "Railway CLI: NOT FOUND"
command -v netlify && echo "Netlify CLI: OK" || echo "Netlify CLI: NOT FOUND"
command -v python3 && echo "Python 3: OK" || echo "Python 3: NOT FOUND"
command -v node && echo "Node.js: OK" || echo "Node.js: NOT FOUND"
```

```
AskUserQuestion:
  question: "How would you like to deploy?"
  options:
    - label: "Full deploy (Railway + Netlify)"
      description: "Deploy backend to Railway and frontend to Netlify — requires both CLIs"
    - label: "Local preview"
      description: "Run backend locally with uvicorn, open frontend in dev mode — no cloud CLIs needed"
    - label: "Generate artifacts only"
      description: "Stage all files for manual deployment — no CLI calls"
```

## Step 3: Stage Data for Deployment

Copy council output into the evaluator service directory so it can serve the data:

```bash
# Create council-out directory in evaluator service
mkdir -p production/backend/evaluator/council-out

# Copy the evaluated project data
cp -r council-out/$SLUG production/backend/evaluator/council-out/$SLUG

echo "Staged data for $SLUG:"
find production/backend/evaluator/council-out/$SLUG -type f | head -20
```

## Step 4: Deploy Backend

### Option A: Railway Deploy

```bash
cd production
bash deploy.sh $SLUG
```

### Option B: Local Preview

```bash
# Install dependencies
cd production/backend/evaluator
pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt

# Set the council-out path to the repo's council-out
export COUNCIL_OUT_DIR=../../../council-out

# Start the evaluator (it has all the dashboard endpoints)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
echo "Backend running at http://localhost:8000"
echo "Health: http://localhost:8000/health"
echo "Dashboard API: http://localhost:8000/dashboard/$SLUG"
echo "Ostrom Radar: http://localhost:8000/evaluate/$SLUG/ostrom-radar"
```

## Step 5: Deploy Frontend

### Option A: Netlify Deploy

```bash
cd production/frontend

# Set API URL to Railway evaluator
echo "NEXT_PUBLIC_API_URL=https://YOUR_RAILWAY_URL" > .env.production.local

npm install
npm run build
netlify deploy --prod --dir=out
```

### Option B: Local Preview

```bash
cd production/frontend

# Set API URL to local backend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm install
npm run dev &
echo "Frontend running at http://localhost:3000"
echo "Project page: http://localhost:3000/project/?slug=$SLUG"
```

## Step 6: Print Live URLs

```
=== OptInPG Production Deployment ===

Project: $SLUG

Backend:
  Evaluator API: [URL]/health
  Dashboard API: [URL]/dashboard/$SLUG
  Ostrom Radar:  [URL]/evaluate/$SLUG/ostrom-radar
  EAS Data:      [URL]/evaluate/$SLUG/eas
  Full Report:   [URL]/evaluate/$SLUG/report

Frontend:
  Dashboard:     [URL]
  Project view:  [URL]/project/?slug=$SLUG

EAS Attestation:
  Attestation data: council-out/$SLUG/synth/eas-attestations.json
  Attest on Base:   Use the "Attest on Base" button on the dashboard

Council Output:
  Data:      council-out/$SLUG/data/
  Evals:     council-out/$SLUG/eval/
  Synthesis: council-out/$SLUG/synth/
```
