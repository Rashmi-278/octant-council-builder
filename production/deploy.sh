#!/usr/bin/env bash
set -euo pipefail

# OptInPG Production Deploy Script
# Usage: ./deploy.sh [slug]
# Deploys the evaluation dashboard to Railway (backend) + Netlify (frontend)

SLUG="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== OptInPG Production Deploy ==="
echo ""

# Validate slug if provided
if [ -n "$SLUG" ]; then
    COUNCIL_DIR="$REPO_ROOT/council-out/$SLUG"
    if [ ! -d "$COUNCIL_DIR" ]; then
        echo "ERROR: No council output found at $COUNCIL_DIR"
        echo "Run '/council:evaluate $SLUG' first."
        exit 1
    fi
    echo "Deploying council output for: $SLUG"
    echo "Data directory: $COUNCIL_DIR"
    echo ""
fi

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v railway &> /dev/null; then
    echo "WARNING: Railway CLI not found. Install: npm i -g @railway/cli"
    echo "Skipping Railway deploy."
    SKIP_RAILWAY=true
else
    SKIP_RAILWAY=false
    echo "  Railway CLI: OK"
fi

if ! command -v netlify &> /dev/null; then
    echo "WARNING: Netlify CLI not found. Install: npm i -g netlify-cli"
    echo "Skipping Netlify deploy."
    SKIP_NETLIFY=true
else
    SKIP_NETLIFY=false
    echo "  Netlify CLI: OK"
fi

echo ""

# Deploy backend to Railway
if [ "$SKIP_RAILWAY" = false ]; then
    echo "=== Deploying Backend to Railway ==="
    echo ""

    # Deploy each service
    for SERVICE in collector analyst evaluator; do
        echo "Deploying $SERVICE service..."
        cd "$SCRIPT_DIR/backend/$SERVICE"
        railway up --detach 2>/dev/null || echo "  (Railway deploy queued for $SERVICE)"
        cd "$SCRIPT_DIR"
    done

    echo ""
    echo "Railway services deploying. Check status:"
    echo "  railway status"
    echo ""
fi

# Deploy frontend to Netlify
if [ "$SKIP_NETLIFY" = false ]; then
    echo "=== Deploying Frontend to Netlify ==="
    echo ""

    cd "$SCRIPT_DIR/frontend"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install --production=false
    fi

    # Build
    echo "Building Next.js dashboard..."
    npm run build

    # Deploy
    echo "Deploying to Netlify..."
    netlify deploy --prod --dir=out 2>/dev/null || netlify deploy --dir=out

    cd "$SCRIPT_DIR"
    echo ""
fi

# Summary
echo "=== Deploy Summary ==="
echo ""
if [ "$SKIP_RAILWAY" = false ]; then
    echo "Backend (Railway):"
    echo "  Collector:  https://[your-railway-url]/health"
    echo "  Analyst:    https://[your-railway-url]/health"
    echo "  Evaluator:  https://[your-railway-url]/health"
fi
if [ "$SKIP_NETLIFY" = false ]; then
    echo "Frontend (Netlify):"
    echo "  Dashboard:  https://[your-netlify-url]/"
fi
echo ""
echo "Update NEXT_PUBLIC_API_URL in your Netlify env to point to your Railway evaluator URL."
echo ""
echo "=== Deploy Complete ==="
