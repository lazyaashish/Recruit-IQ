# RecruitIQ

**RecruitIQ** is a resume-to-job match intelligence platform. Upload a resume and a job description, and get instant match scoring, skill gap analysis, a personalized learning roadmap, and tailored interview questions.

## Stack

- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Vercel (frontend static build + Python serverless functions)

---

## Project Structure

```
recruitiq/
├── api/                  # Vercel serverless entry point
│   ├── index.py
│   └── requirements.txt
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Business logic (scoring, parsing, LLM)
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/             # Vite + React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
└── vercel.json
```

---

## Local Development

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # edit SECRET_KEY and DATABASE_URL
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

---

## Deploy to Vercel

1. Push this repo to GitHub.
2. Import the project in [vercel.com](https://vercel.com) — select the **root** folder (where `vercel.json` lives).
3. Set the following **Environment Variables** in Vercel project settings:

| Variable | Description |
|---|---|
| `SECRET_KEY` | Strong random string — `openssl rand -hex 32` |
| `DATABASE_URL` | Postgres connection string (e.g. from Neon / Supabase) |
| `ENVIRONMENT` | `production` |
| `CORS_ORIGINS_STR` | Your Vercel deployment URL(s), comma-separated |
| `LLM_PROVIDER` *(optional)* | `openai` or `anthropic` |
| `LLM_API_KEY` *(optional)* | API key for the chosen LLM provider |
| `LLM_MODEL` *(optional)* | e.g. `gpt-4o-mini` or `claude-haiku-4-5-20251001` |

4. Click **Deploy**. Vercel builds the frontend and deploys the Python API as serverless functions automatically.

> **Note:** Without `LLM_PROVIDER` / `LLM_API_KEY`, the app operates in rule-based mode (no LLM enrichment) — all core features still work.

---

## Environment Variables Reference

Copy `backend/.env.example` → `backend/.env` for local development.

---

## License

MIT
