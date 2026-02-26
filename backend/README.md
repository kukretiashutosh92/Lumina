LuminaLib Backend

The LuminaLib Backend is a FastAPI-based REST API that powers the LuminaLib library management system. It provides authentication, book management, borrowing workflows, review handling, recommendation logic, file storage abstraction, and LLM-powered analysis features.
This backend is built with scalability, modularity, and extensibility in mind. It supports pluggable storage systems and language model providers, making it flexible for development and production environments.

Technology Stack
The backend uses the following technologies:
Core Framework
•	FastAPI (v0.109.2)
•	Uvicorn (ASGI server)
Database
•	PostgreSQL
•	SQLAlchemy (Async ORM)
•	asyncpg (PostgreSQL async driver)
•	Alembic (Database migrations)
Authentication
•	JWT (JSON Web Tokens)
•	Passlib (Password hashing)
Machine Learning
•	scikit-learn (TF-IDF and similarity-based recommendations)
AI / LLM Integration
Pluggable LLM providers:
•	Mock provider (for development and testing)
•	Ollama (local LLM hosting)
•	OpenAI API
File Storage
Pluggable storage backends:
•	Local filesystem storage
•	Amazon S3

Features
The backend provides the following major capabilities:
•	User authentication (signup, login, JWT-based protection)
•	Profile management
•	Book CRUD operations
•	File uploads (PDF/Text)
•	Borrow and return workflow
•	Book reviews and ratings
•	Hybrid recommendation engine (ML + optional LLM)
•	AI-powered book analysis and suggestions
•	Modular LLM and storage abstraction layers

Setup Instructions
You can run the backend using Docker or locally for development.

Option 1: Using Docker
Refer to the main project README.md in the root directory for docker-compose instructions.
Docker will automatically:
•	Start PostgreSQL
•	Apply migrations
•	Launch the FastAPI server

Option 2: Local Development Setup
Follow these steps to run the backend locally.
1. Install Dependencies
Navigate to the backend directory and create a virtual environment:
cd backend
python -m venv .venv
Activate the virtual environment:
On macOS/Linux:
source .venv/bin/activate
On Windows:
.venv\Scripts\activate
Install required dependencies:
pip install -r requirements.txt

2. Configure Environment Variables
Copy the example environment file:
cp .env.example .env
Open the .env file and update the values according to your setup.

3. Run Database Migrations
Ensure PostgreSQL is running, then execute:
alembic upgrade head
This will create all required database tables.

4. Start the Development Server
Run:
uvicorn app.main:app --reload
The API will be available at:
http://localhost:8000

Environment Configuration
Below are the most important environment variables. Refer to .env.example for a complete list.

Database Configuration
DB_URL=postgresql+asyncpg://user:password@localhost:5432/luminalib
This defines the asynchronous database connection string.

Authentication Configuration
SECRET_KEY=your-secret-key-here
Used for signing JWT tokens.
In production, this must be a secure, randomly generated value.

Storage Backend Configuration
Select the storage backend:
STORAGE_BACKEND=local
Options:
•	local
•	s3
Local Storage
LOCAL_STORAGE_PATH=./uploads
Files will be saved to this directory.
Amazon S3 Storage
AWS_BUCKET=your-bucket-name
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

LLM Provider Configuration
Select the LLM provider:
LLM_PROVIDER=mock
Options:
•	mock
•	ollama
•	openai

Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
Requires Ollama to be running locally.

OpenAI Configuration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
Requires a valid OpenAI API key.

Recommendation Engine Configuration
RECOMMENDATION_ENGINE=hybrid
Options:
•	hybrid (ML + LLM ranking)
•	llm (LLM-only suggestions)

API Documentation
Once the server is running, interactive API documentation is available at:
Swagger UI:
http://localhost:8000/docs
ReDoc:
http://localhost:8000/redoc
These interfaces allow you to:
•	Explore all endpoints
•	Test requests directly
•	View request/response schemas
•	Authenticate using JWT tokens

Code Quality and Linting
The project uses Ruff for linting and formatting.
Run checks:
ruff check .
Format code:
ruff format .
Auto-fix issues:
ruff check --fix .
Configuration is defined in:
pyproject.toml

Project Structure
Below is an overview of the backend folder structure.
backend/
│
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── books.py
│   │   └── recommendations.py
│   │
│   ├── llm/
│   │   ├── mock.py
│   │   ├── ollama.py
│   │   └── openai.py
│   │
│   ├── storage/
│   │   ├── local.py
│   │   └── s3.py
│   │
│   ├── models.py
│   ├── schemas.py
│   ├── deps.py
│   ├── database.py
│   └── main.py
│
├── alembic/
├── tests/
├── requirements.txt
└── .env.example

