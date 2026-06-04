# Agentic Go Contributor

![CI](https://github.com/Pranavsingh431/agentic-go-contributor/actions/workflows/backend-ci.yml/badge.svg)

An AI agent that reads a GitHub issue from a Go open-source repo,
plans a fix, generates a patch, runs go test, and produces a PR summary.

## Architecture

```
GitHub Issue → Fetch → Clone → Map → Plan (LLM) → Patch (LLM) → go test
```

## Stack

- Backend: FastAPI + Python, deployed on Render
- Frontend: React + Vite, deployed on Vercel
- LLM: anthropic/claude-sonnet-4-5 via OpenRouter
- Target repo: spf13/cobra

## Run Locally

**Backend:**
```bash
cd backend
cp .env.example .env   # fill in OPENROUTER_API_KEY and GITHUB_TOKEN
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Run Evals

```bash
python -m evals.run_eval
```

## Tests

```bash
cd backend && python -m pytest tests/ -v
```

## Deploy

**Backend:** connect repo to Render, use `render.yaml`

**Frontend:** connect repo to Vercel, set root to `frontend/`

Backend live: https://agentic-go-contributor.onrender.com

Frontend live: https://agentic-go-contributor.vercel.app
