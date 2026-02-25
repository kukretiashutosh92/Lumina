LuminaLib

Library app with authentication, book upload, borrow/return, reviews, LLM summary and sentiment analysis, and recommendations.

Quick Start

From project root run:

docker compose up --build

This will start:

FastAPI backend on port 8000
Next.js frontend on port 3000
PostgreSQL on port 5432
LLM provider (mock by default)

Open in browser:

http://localhost:3000

You can sign up, add books (optional file upload), borrow/return books, and leave reviews.

Summaries and review analysis run in the background.

Using Ollama

If using built-in Ollama service from docker-compose:

Start the stack:

docker compose up --build

Pull the model:

docker compose exec ollama ollama pull llama3.2

Verify Ollama:

curl http://localhost:8000/health/ollama

The model is cached in the ollama_data volume.
You only need to pull once unless the volume is removed.

Configuration

Backend:

Copy:

backend/.env.example to backend/.env

Set variables:

Database:

DB_URL=postgresql+asyncpg://luminalib:luminalib@db:5432/luminalib

Security:

SECRET_KEY=your-secret-key

Storage:

For local:

STORAGE_BACKEND=local

For S3:

STORAGE_BACKEND=s3
AWS_BUCKET=your-bucket
AWS_REGION=your-region

LLM Provider

Set:

LLM_PROVIDER=mock

Options:

mock
ollama
openai

For OpenAI:

OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini

Frontend (if not using Docker)

Set:

NEXT_PUBLIC_API_URL=http://localhost:8000

Swapping Storage or LLM

You can change file storage or LLM provider using environment variables only.
No code changes required.

Storage options:

local
s3

LLM options:

mock
ollama
openai

Database Migrations (Alembic)

From backend folder:

cd backend
alembic upgrade head

To create new migration:

alembic revision --autogenerate -m "description"
alembic upgrade head

If tables already exist and you get DuplicateTable error:

alembic stamp 001
alembic upgrade head

Run Without Docker

Start PostgreSQL and create database:

luminalib

Backend:

cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

Frontend:

cd frontend
npm install
npm run dev

Set:

NEXT_PUBLIC_API_URL=http://localhost:8000

Code Quality

Backend:

cd backend
ruff check .
ruff format .

Frontend:

npm run lint
npm test