# RecruitIQ

**RecruitIQ** is an AI-powered resume-to-job match intelligence platform. Upload a resume and a job description, then get a match score, skill-gap analysis, learning roadmap and tailored interview questions .
## Live Demo

🔗 https://recruitt-iq.vercel.app/login
## What it does

RecruitIQ helps users:

- Upload resumes in **PDF, DOCX, or TXT**
- Create and manage job descriptions
- Compare a resume against a job description
- View a detailed score breakdown with matching and missing skills
- Generate a personalized learning roadmap for you.
- Generate interview questions.
- Export analysis results as **Markdown** or **PDF**
- View dashboards and history for past analyses

## Features

- **Resume parsing** with contact info extraction
- **Job description parsing** with required skill extraction
- **Semantic matching** and keyword coverage scoring
- **Skill overlap analysis** for matched / missing / extra skills
- **Learning roadmap generation** with phases, milestones, and quick wins
- **Interview prep pack** with technical, behavioral, and system design
- **JWT authentication** for user accounts
- **Analysis history** and dashboard insights
- **Export support** for sharing reports
- **Optional LLM enrichment** when configured
## Tech Stack

### Frontend
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts
- react-dropzone
- react-hot-toast
- Lucide Icons

### Backend
- FastAPI
- SQLAlchemy
- SQLite for local development
- PostgreSQL for production
- JWT authentication
- Pydantic / Pydantic Settings
- pdfplumber
- python-docx
- scikit-learn
- sentence-transformers
- structlog

### Deployment
- Vercel frontend static build
- Vercel Python serverless API

## How it works

1. A user signs up or logs in.
2. The user uploads a resume.
3. The user adds a job description.
4. RecruitIQ analyzes both documents.
5. The app returns:
   - overall match score
   - semantic score
   - keyword score
   - skill overlap
   - missing skills
   - suggestions
   - learning roadmap
   - interview questions
6. The user can export the result as Markdown or PDF format.

## Project Structure

```text
recruitiq/
├── api/                  # Vercel serverless entry point
│   ├── index.py
│   └── requirements.txt
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── services/     # Parsing, scoring, roadmap, interview generation
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── requirements.txt
├── frontend/             # Vite + React app
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── utils/
│   └── package.json
├── vercel.json
└── README.md
```

## Local Development

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`.

### 3) Connect frontend to backend

By default, the frontend calls `/api/v1`.

For local development, you can set:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

or keep the default if you are serving both behind the same domain.

## Environment Variables

### Root / production example

Copy `.env.example` to `.env` and fill in the values:

```env
SECRET_KEY=your-strong-secret
DATABASE_URL=sqlite:///./recruitiq.db
ENVIRONMENT=production
CORS_ORIGINS_STR=http://localhost:5173,http://localhost:3000
LLM_PROVIDER=openai
LLM_API_KEY=your_api_key
LLM_MODEL=gpt-4o-mini
VITE_API_URL=http://localhost:8000/api/v1
```

### Backend env vars

The backend supports these settings:

- `APP_NAME`
- `DEBUG`
- `ENVIRONMENT`
- `SECRET_KEY`
- `DATABASE_URL`
- `EMBEDDING_MODEL`
- `EMBEDDING_DEVICE`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_BASE_URL`
- `LOG_LEVEL`
- `CORS_ORIGINS_STR`

### Important notes

- If `LLM_PROVIDER` and `LLM_API_KEY` are not set, RecruitIQ uses a **deterministic rule-based fallback**.
- Local development uses **SQLite** by default.
- Production should use a hosted **PostgreSQL** database.
- Resume uploads support **PDF, DOCX, and TXT** files up to **5 MB**.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Resumes
- `POST /api/v1/resumes/upload`
- `GET /api/v1/resumes/`
- `DELETE /api/v1/resumes/{resume_id}`

### Job Descriptions
- `POST /api/v1/jobs/`
- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/{job_id}`
- `DELETE /api/v1/jobs/{job_id}`

### Analysis
- `POST /api/v1/analysis/`
- `GET /api/v1/analysis/`
- `GET /api/v1/analysis/{analysis_id}`
- `GET /api/v1/analysis/dashboard`

### Export
- `GET /api/v1/export/{analysis_id}/markdown`
- `GET /api/v1/export/{analysis_id}/pdf`

### Meta
- `GET /health`
- `GET /docs`
- `GET /redoc`

## Deployment on Vercel

1. Push this repository to GitHub.
2. Import the project in Vercel.
3. Use the **root** folder as the project root.
4. Add the required environment variables in Vercel settings.
5. Deploy.

The `vercel.json` file configures:

- the React frontend as a static build
- the FastAPI backend as Python serverless
- routing for `/api/v1`, `/docs`, `/redoc`, and `/health`

## Testing

Backend tests are included under `backend/tests/`.

Run them with:

```bash
cd backend
pytest
```
##tempory data 
## License

MIT
