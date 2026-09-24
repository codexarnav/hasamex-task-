# InsightOS — Qualitative Research Intelligence Platform

> **AI-powered qualitative research platform designed to extract, analyze, compare, and synthesize insights from expert interview transcripts and interview guides with strict, unbreakable provenance and anti-hallucination guarantees.**

---

## 🌐 LIVE LINKS — Production Ready

- **Live Web Application (Vercel):** [https://hasamex-task-17y3.vercel.app](https://hasamex-task-17y3.vercel.app/)
- **Backend API (Render):** [https://hasamex-task.onrender.com](https://hasamex-task.onrender.com/)
- **API Docs (Swagger UI):** [https://hasamex-task.onrender.com/docs](https://hasamex-task.onrender.com/docs)
- **API ReDoc:** [https://hasamex-task.onrender.com/redoc](https://hasamex-task.onrender.com/redoc)
- **Health Check:** [https://hasamex-task.onrender.com/health](https://hasamex-task.onrender.com/health)
- **Status:** `100% Operational`


## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check for hosting monitoring |
| `GET` | `/api/v1/projects` | List all research projects |
| `POST` | `/api/v1/projects` | Create a new research project |
| `GET` | `/api/v1/projects/{id}` | Get project details, stats, and metadata |
| `POST` | `/api/v1/projects/{id}/guide` | Upload interview guide & extract research questions |
| `GET` | `/api/v1/projects/{id}/questions` | List extracted research questions |
| `POST` | `/api/v1/projects/{id}/transcripts` | Upload transcript (PDF/TXT) & ingest into vector DB |
| `GET` | `/api/v1/projects/{id}/transcripts` | List all project transcripts and parsing status |
| `DELETE` | `/api/v1/transcripts/{id}` | Delete a transcript and clean up associated vectors |
| `POST` | `/api/v1/projects/{id}/analyze` | Trigger full AI analysis pipeline (all or selected transcripts) |
| `GET` | `/api/v1/projects/{id}/evidence` | Retrieve grounded evidence with utterance citations |
| `GET` | `/api/v1/projects/{id}/differences` | Retrieve cross-expert difference analysis |
| `GET` | `/api/v1/projects/{id}/insights` | Retrieve synthesized strategic insights |
| `POST` | `/api/v1/projects/{id}/copilot` | Ask exploratory research questions via Copilot |

---

## 🛠️ Tech Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons
- **Backend:** Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x (Async), Alembic, Uvicorn
- **AI & Orchestration:** LangGraph, Google Gemini 2.5 Flash, Gemini Embeddings (`gemini-embedding-2`)
- **Vector DB:** Qdrant Cloud (Cosine Similarity, Payload Filtering)
- **Database:** PostgreSQL 16 (AsyncPG, UUID keys, UTC timestamps)
- **Document Parsing:** PyMuPDF, pdfplumber, Tesseract OCR, Pillow
- **Cloud Infrastructure:** Vercel (Frontend), Render (FastAPI Web Service + PostgreSQL), Qdrant Cloud

---

## 💻 Local Setup & Development

### Prerequisites
- Python 3.12+
- Node.js 18+ & npm
- PostgreSQL 16
- Qdrant (Docker or Cloud instance)
- Google Gemini API Key

---

### Option A: Quick Start with Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/codexarnav/hasamex-task-.git
cd hasamex-task-

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY

# 3. Start all services (Backend, Postgres, Qdrant)
cd backend
docker compose up --build
```
- API is available at: `http://localhost:8000`
- Swagger UI at: `http://localhost:8000/docs`

---

### Option B: Manual Local Setup

#### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and configure your DATABASE_URL, QDRANT_URL, and GEMINI_API_KEY

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Start development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Running Tests

```bash
cd backend
pytest -v
```


**Built with precision for Qualitative Research Intelligence | InsightOS v1.0**
