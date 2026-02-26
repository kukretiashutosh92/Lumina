Docker Guide – LuminaLib
All commands must be executed from the project root directory (the folder containing docker-compose.yml).

Prerequisites
Make sure the following are installed:
•	Docker (v24+ recommended)
•	Docker Compose (v2+ recommended)
•	Minimum 4GB RAM available for Docker (recommended for Ollama)
Verify installation:
docker --version
docker compose version

Services Overview
When running the stack, the following services start:
Service	Description	Host Port
frontend	Next.js React frontend	3000
api	FastAPI backend	8000
db	PostgreSQL database	5433
ollama	Local LLM service	11434

Start Everything
docker compose up --build
This will:
•	Build images (if not already built)
•	Start all services
•	Automatically run database migrations (alembic upgrade head)
•	Start API and frontend
Access the services:
Frontend:
http://localhost:3000
API:
http://localhost:8000
API Docs:
http://localhost:8000/docs
PostgreSQL:
Host: localhost
Port: 5433
User: luminalib
Password: luminalib
Database: luminalib

Run in Background (Detached Mode)
docker compose up --build -d
Containers will run in the background.

View Logs
View logs for all services:
docker compose logs -f
View logs for a specific service:
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f db
docker compose logs -f ollama

Stop Services
docker compose down
This stops containers but keeps volumes (database + Ollama models).

Stop and Remove Everything (Fresh Start)
docker compose down -v
This removes:
•	Database data
•	Ollama model cache
•	All volumes
Start fresh again:
docker compose up --build

Rebuild After Code Changes
If backend or frontend code changes:
docker compose up --build
Rebuild only one service:
docker compose up --build api
docker compose up --build frontend

Database Behavior
•	Migrations run automatically when the API starts.
•	If you run docker compose down -v, the database will reset.
•	Internal PostgreSQL port: 5432
•	Exposed host port: 5433
Connect using any DB client:
Host: localhost
Port: 5433
User: luminalib
Password: luminalib
Database: luminalib

Ollama (AI Features)
The stack runs Ollama inside Docker, so no host installation is required.
This avoids:
•	Host networking issues
•	Snap configuration problems
•	OLLAMA_HOST binding issues
•	Firewall configuration problems

First-Time Startup
docker compose up --build
On first run:
•	The ollama container checks for llama3.2
•	If not present, it downloads automatically
•	Model is stored in ollama_data Docker volume
Subsequent runs skip model download.

Verify Ollama
curl http://localhost:8000/health/ollama
Possible responses:
Working:
{"ollama":"ok","model_loaded":true}
Not reachable:
{"ollama":"unavailable","detail":"..."}
Mock mode:
{"ollama":"not_used","llm_provider":"mock"}

Switching LLM Providers
Use Mock LLM (No AI)
In docker-compose.yml:
LLM_PROVIDER=mock
Then rebuild:
docker compose up --build

Use OpenAI Instead
Set environment variables in api service:
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o-mini
Then rebuild containers.

Use Host Ollama Instead of Docker Ollama
If running Ollama locally on host:
1.	Remove ollama service from docker-compose.yml
2.	Set for api service:
OLLAMA_BASE_URL=http://host.docker.internal:11434
3.	Add:
extra_hosts:
  - "host.docker.internal:host-gateway"
4.	Ensure host Ollama listens on 0.0.0.0
Using Docker Ollama is recommended to avoid networking issues.

Why AI Recommendations May Not Appear
Similar Books (Book Page):
•	Requires Ollama running
•	If Ollama is down → returns empty suggestions
"You Might Also Like":
•	Requires at least one genre preference
•	Uses hybrid or LLM ranking
"In Your Library":
•	Requires added books
•	Requires genre preferences
If empty:
•	Add books
•	Add genre preferences
•	Check Ollama health

Troubleshooting
Check Running Containers
docker ps
Enter a Container
API container:
docker compose exec api bash
Database container:
docker compose exec db psql -U luminalib -d luminalib
Clean Rebuild Everything
docker compose down -v
docker system prune -f
docker compose up --build

Production Recommendations
For production deployment:
•	Use managed PostgreSQL (AWS RDS / Cloud SQL)
•	Use S3 for file storage
•	Run behind reverse proxy (Nginx / Traefik / IIS)
•	Enable HTTPS
•	Set strong SECRET_KEY
•	Disable debug mode
•	Scale API containers if needed

