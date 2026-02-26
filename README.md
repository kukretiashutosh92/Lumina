LuminaLib
LuminaLib is a full-stack Library Management Application built with:
•	FastAPI (Backend API)
•	Next.js (React) (Frontend)
•	PostgreSQL (Database)
•	LLM Integration (Mock / Ollama / OpenAI)
•	Hybrid Recommendation Engine
Features
•	JWT-based User Authentication
•	Add books (with optional file upload)
•	Borrow / Return books
•	Review and rating system
•	LLM-generated book summaries
•	Review sentiment + consensus analysis
•	Hybrid & LLM-based recommendations
•	Config-driven storage & LLM provider switching

Architecture Overview
Frontend (Next.js)
⬇
FastAPI REST API
⬇
PostgreSQL Database
Optional Services:
•	Ollama (Local LLM)
•	OpenAI API
•	S3 Storage
The system is fully configurable via environment variables. No code changes required when switching providers.

Quick Start (Docker - Recommended)
From project root:
docker compose up --build
This starts:
•	FastAPI API → http://localhost:8000
•	Next.js Frontend → http://localhost:3000
•	PostgreSQL → port 5432
•	LLM provider (mock by default or Ollama if configured)
Open in browser:
http://localhost:3000
Steps:
1.	Sign up
2.	Add books
3.	Borrow / Return books
4.	Leave reviews
Summaries and review analysis run asynchronously in the background.

Using Ollama (Local LLM)
If using built-in Ollama service from docker-compose:
1. Start stack
docker compose up --build
2. Pull model (run once)
docker compose exec ollama ollama pull llama3.2
3. Verify health
curl http://localhost:8000/health/ollama
The model is cached in the ollama_data volume.

Configuration
Backend Setup
Copy:
backend/.env.example
To:
backend/.env
Then configure the following variables.

Database
DB_URL=postgresql+asyncpg://luminalib:luminalib@db:5432/luminalib
For local setup, update host if needed.

Security
SECRET_KEY=your-secret-key
Used for JWT signing. Change in production.

Storage Backend
Local (Default)
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./uploads
Amazon S3
STORAGE_BACKEND=s3
AWS_BUCKET=your-bucket-name
AWS_REGION=us-east-1
Uses boto3 internally.

LLM Configuration
Set:
LLM_PROVIDER=mock
Available options:
Mock (Default)
LLM_PROVIDER=mock
No external API calls. Used for development.

Ollama
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434

OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

Recommendation Engine
RECOMMENDATION_ENGINE=hybrid
Options:
hybrid (Default)
Combines:
•	Preference matching
•	Collaborative filtering
•	TF-IDF similarity
llm
Uses LLM to rank and suggest recommendations.

Storage and LLM Swapping
You can switch:
•	Storage backend
•	LLM provider
•	Recommendation engine
By updating environment variables only. No code changes required.

Database Migrations (Alembic)
From backend folder:
cd backend
alembic upgrade head
Create new migration:
alembic revision --autogenerate -m "description"
alembic upgrade head
If tables already exist and you get DuplicateTable:
alembic stamp 001
alembic upgrade head

Run Without Docker
1. Setup PostgreSQL
Create database:
luminalib

2. Start Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
Backend runs on:
http://localhost:8000

3. Start Frontend
cd frontend
npm install
npm run dev
Set:
NEXT_PUBLIC_API_URL=http://localhost:8000
Frontend runs on:
http://localhost:3000

API Highlights
•	JWT Authentication
•	Async database operations
•	Background LLM processing
•	Health check endpoints
•	Modular service layer
•	Config-based provider switching

Code Quality
Backend
cd backend
ruff check .
ruff format .

Frontend
cd frontend
npm run lint
npm test

Production Notes
•	Change SECRET_KEY
•	Use managed PostgreSQL in production
•	Use S3 instead of local storage
•	Use OpenAI or production LLM instead of mock
•	Run behind reverse proxy (Nginx / IIS / Traefik)
•	Enable HTTPS

