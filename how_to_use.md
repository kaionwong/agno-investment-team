# How to Run the Investment Team

Run the entire stack using Docker with official PostgreSQL image that includes pgvector.

# Docker Deployment

Run the entire stack in Docker containers.

## Prerequisites

- **Docker Desktop** installed and running
- **Ollama** running locally with `llama3.2` and `nomic-embed-text` models pulled
- **API Key**: Get free `EXA_API_KEY` at https://exa.ai

## Quick Start

```powershell
# 1. Navigate to project directory
cd agno-investment-team

# 2. Create .env file with your credentials
cp example.env .env

# Edit .env and set:
#   OLLAMA_BASE_URL=http://localhost:11434
#   EXA_API_KEY=your_key_from_exa.ai
#   DB_HOST=investment-team-db  (Docker service name)
#   DB_PORT=5432
#   DB_USER=postgres
#   DB_PASS=postgres
#   DB_DATABASE=agno_investment_team

# 3. Start everything (API + PostgreSQL containers)
# Build images fresh (no cache); once or only when needed
docker compose build --no-cache

# Start containers
docker compose up -d

# 4. Load research into knowledge base (in a new PowerShell window)
docker exec -it investment-team-api python -m app.load_knowledge

# 5. Open UI
# Browser → https://os.agno.com
# Click "Add OS" → "Local" → "http://localhost:8000"
```

**Done!** Your investment team is running. Skip to [Testing](#testing-the-system).

## Understanding the Docker Database Setup

When you run `docker compose up -d --build`, here's what happens automatically:

| Component | What Docker Does | Your DB Credentials |
|-----------|------------------|-------------------|
| **Database Container** | Spins up PostgreSQL 16 with pgvector pre-installed | User: `postgres` |
| | Creates `agno_investment_team` database | Pass: `postgres` (default) |
| | Enables pgvector extension automatically | Host: `investment-team-db` |
| **API Container** | Connects to database using `.env` credentials | Loads on startup |
| | Creates tables (team_knowledge, learnings, sessions) | Uses DB_* variables |
| | Ready to receive knowledge base data | |

**You don't need to manually:**
- Create the database ✗ (Docker does it)
- Install pgvector extension ✗ (pre-built in image)
- Set up user credentials ✗ (defaults in compose.yaml)

## Detailed Steps

### Step 1: Prepare Environment

```powershell
# Create .env file
cp example.env .env

# Edit with your values:
# - OLLAMA_BASE_URL=http://localhost:11434
# - EXA_API_KEY=your_key
# - DB credentials (defaults: postgres/postgres)
```

### Step 2: Start Docker Containers

```powershell
# Build and start all services
docker compose up -d --build

# Verify services are running
docker ps

# Check API logs
docker logs investment-team-api -f

# Check database logs
docker logs investment-team-db -f
```

### Step 2.5: Verify Database Setup (Automatic)

Docker automatically creates the database and extensions for you. Here's what happens:

✅ **Automatic setup by Docker:**
- Database `agno_investment_team` is created automatically
- pgvector extension is pre-installed in the Docker image
- Tables are created when the API first connects

**Verify database is ready:**

```powershell
# Check if database is initialized
docker exec investment-team-db psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='agno_investment_team';"

# Should output:
# agno_investment_team

# Verify pgvector extension
docker exec investment-team-db psql -U postgres -d agno_investment_team -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Should output:
# CREATE EXTENSION

# List all tables in the database
docker exec investment-team-db psql -U postgres -d agno_investment_team -c "\dt"
```

If these commands fail, wait 10-15 seconds for the database to fully initialize, then try again.

### Step 4: Initialize Knowledge Base

```powershell
# In a new PowerShell window, load research documents
docker exec -it investment-team-api python -m app.load_knowledge

# Verify output shows loaded documents:
# ✓ Loaded: aapl_profile.md
# ✓ Loaded: msft_profile.md
# ... etc
```

### Step 5: Connect to UI

1. Open browser: https://os.agno.com
2. Click "Add OS" → "Local"
3. Enter `http://localhost:8000`
4. Click "Connect"

---

## Stopping Docker (Method 1)

```powershell
# Stop containers (data persists)
docker compose down

# Stop and remove all data
docker compose down -v

# View current containers
docker ps -a
```

---

# Method 2: Local Terminal + Python venv

Run the API locally in a Python virtual environment. PostgreSQL must be installed locally.

## Prerequisites

- **Python 3.12+** installed and in PATH
- **PostgreSQL 15+** installed and running locally
- **Ollama** running locally with models: `llama3.2`, `nomic-embed-text`
- **API Key**: Get free `EXA_API_KEY` at https://exa.ai

## Verify Prerequisites

```powershell
# Check Python
python --version           # Should be 3.12+

# Check Ollama is running
Get-Process ollama         # Should show the process

# Check Ollama is listening
netstat -ano | findstr "11434"  # Should show LISTENING

# Check PostgreSQL is running
Get-Service *Postgre*      # Should show "Running"

# Verify Ollama models are pulled
ollama list
# Should show:
#   llama3.2           latest
#   nomic-embed-text   latest
```

## Quick Start (Copy-Paste Terminal Sequence)

```powershell
# 1. Activate virtual environment (from your local drive)
C:\Users\<<some_user>>\Dev\virtual_env\venv_agno_investment_team\Scripts\Activate.ps1

# 2. Navigate to the project (in OneDrive)
cd "C:\Users\<<some_user>>\<<some_drive>>\_work\project\etl_for_testing\agno-investment-team"

# 3. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Create .env file
cp example.env .env

# Edit .env and set:
#   OLLAMA_BASE_URL=http://localhost:11434
#   EXA_API_KEY=your_key_from_exa.ai
#   DB_HOST=localhost
#   DB_PORT=5432
#   DB_USER=postgres
#   DB_PASS=your_postgres_password
#   DB_DATABASE=agno_investment_team

# 5. Create the database (run once)
psql -U postgres -c "CREATE DATABASE agno_investment_team;"
psql -U postgres -d agno_investment_team -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 6. Load research into database
python -m app.load_knowledge

# 7. Start the API (keep this terminal open)
python -m app.main

# 8. In a new PowerShell: browse to https://os.agno.com
# Click "Add OS" → "Local" → "http://localhost:8000"
```

**Done!** Your investment team is running locally. Skip to [Testing](#testing-the-system).

## Detailed Steps (venv Method)

### Step 1: Activate Virtual Environment

```powershell
# Activate the venv from your local drive
C:\Users\<<some_user>>\Dev\virtual_env\venv_agno_investment_team\Scripts\Activate.ps1

# Navigate to the project in a cloud drive
cd "C:\Users\<<some_user>>\<<some_drive>>\_work\project\etl_for_testing\agno-investment-team"

# Verify activation (should show prefix in prompt)
# (venv_agno_investment_team) PS C:\Users\<<some_user>>\<<some_drive>>\_work\project\etl_for_testing\agno-investment-team>
```

If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 2: Install/Verify Python Dependencies

```powershell
# Ensure pip is up to date
python -m pip install --upgrade pip

# Install all requirements (may be cached from previous runs)
pip install -r requirements.txt

# Verify key packages
pip list | findstr "agno ollama psycopg pgvector sqlalchemy fastapi"
```

**Expected packages:**
- `agno` - multi-agent framework
- `ollama` - local LLM client
- `psycopg` - PostgreSQL driver
- `pgvector` - vector database support
- `sqlalchemy` - ORM
- `fastapi` - web server
- `python-dotenv` - environment loading
- `yfinance` - financial data
- `exa-py` - web search API

### Step 3: Verify PostgreSQL Connection

```powershell
# Check if PostgreSQL service is running
Get-Service PostgreSQL*

# Test connection
psql -U postgres -c "SELECT 1"
# Should return: 1
```

If PostgreSQL isn't installed:
1. Download from https://www.postgresql.org/download/
2. Install (remember your postgres password)
3. Verify: `Get-Service PostgreSQL*` shows "Running"

### Step 4: Create Database

Use one of these approaches depending on your setup:

**Option 1: Full path to psql (recommended if psql not in PATH)**

```powershell
# Create the database
& "C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -c "CREATE DATABASE agno_investment_team;"

# Enable pgvector extension
& "C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -d agno_investment_team -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify database was created
& "C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -l | findstr "agno_investment_team"
```

Note: The `&` before the path tells PowerShell to invoke the command (required with quoted paths containing spaces).

**Option 2: Direct psql commands (if psql is already in PATH)**

If you already have `psql` in your system PATH, you can use it directly:

```powershell
# Create the database
psql -U postgres -c "CREATE DATABASE agno_investment_team;"

# Enable pgvector extension
psql -U postgres -d agno_investment_team -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Verify database was created
psql -U postgres -l | findstr "agno_investment_team"
```

**Expected result for verification:**
You should see `agno_investment_team` listed in the output.

### Step 5: Configure Environment

Create/update `.env` file in project root:

```bash
# Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Exa API (free key from https://exa.ai)
EXA_API_KEY=your_exa_key_here

# PostgreSQL (local installation)
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=your_postgres_password
DB_DATABASE=agno_investment_team

# Optional: Development
RUNTIME_ENV=dev
AGNO_DEBUG=True
```

The `.env` file is automatically loaded by `app/main.py` and `app/load_knowledge.py`.

### Step 6: Initialize Knowledge Base

```powershell
# With venv activated, load research documents
python -m app.load_knowledge

# Output will show:
# Loading research into PostgreSQL...
# ✓ Loaded: aapl_profile.md
# ✓ Loaded: msft_profile.md
# ✓ Loaded: nvda_profile.md
# ✓ Loaded: ai_semiconductors.md
# ✓ Loaded: cloud_computing.md
# Database ready with 7 company profiles + 2 sector analyses
```

**First run takes 2-5 minutes** (processing + vectorization).

### Step 7: Start the API

```powershell
# With venv activated
python -m app.main

# Output will show:
# INFO:     Application startup complete
# INFO:     Uvicorn running on http://127.0.0.1:8000

# Keep this terminal open - it's the API server
```

### Step 8: Connect to UI

1. **Open browser**: https://os.agno.com
2. **Click**: "Add OS" → "Local"
3. **Enter**: `http://localhost:8000`
4. **Click**: "Connect"

You should see all 7 agents and 4 teams available.

---

# Testing the System

Now that your API is running, test these queries in the UI:

### Test 1: Route Team (Simple Query)
```
What's AAPL's P/E ratio?
```
**Expected**: Market Analyst queries YFinance and returns the ratio.

### Test 2: Coordinate Team (Multi-Agent Analysis)
```
Should we invest in NVIDIA? Consider market, financial, technical, and risk perspectives.
```
**Expected**: All analysts respond; Committee Chair provides final recommendation (BUY/HOLD/PASS).

### Test 3: Broadcast Team (Parallel Evaluation)
```
Full committee review: evaluate TSLA for a $2M investment
```
**Expected**: Each analyst provides independent assessment simultaneously.

### Test 4: Task Team (Autonomous Decomposition)
```
Deploy $10M across the top 5 AI sector stocks with optimization
```
**Expected**: Agents autonomously break down into substeps, research, and propose allocation.

### Test 5: Knowledge Agent (RAG Search)
```
What does our research say about cloud computing trends?
```
**Expected**: Search hybrid index (keyword + semantic) over company profiles and sector analyses.

### Test 6: Investment Workflow (Deterministic Pipeline)
```
Run full investment review on NVIDIA
```
**Expected**: Market → Financial+Technical (parallel) → Risk → Memo Writer → Chair→ Decision memo saved.

---

# Troubleshooting

## Docker Issues

### "Cannot connect to API"
```powershell
# Check if containers are running
docker ps

# View API logs for errors
docker logs investment-team-api

# Restart containers
docker compose restart

# Full rebuild
docker compose down
docker compose up -d --build
```

### "Database connection refused"
```powershell
# Check database container status
docker ps | findstr "investment-team-db"

# Check database logs
docker logs investment-team-db

# Verify port 5432 is exposed
docker ps --format "table {{.Names}}\t{{.Ports}}" | findstr "investment-team-db"

# Restart database
docker compose restart investment-team-db
```

---

## Method 2: venv Issues

### "ModuleNotFoundError: No module named 'agno'"
```powershell
# Ensure venv is activated
.\venv_agno_investment_team\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

### "psycopg.OperationalError: couldn't connect to server"
```powershell
# Verify PostgreSQL is running
Get-Service *Postgre*

# Test connection
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -c "SELECT 1"

# If service is stopped, start it
Start-Service PostgreSQL15

# Check database exists
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -l | findstr "agno_investment_team"

# Recreate if missing
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -c "CREATE DATABASE agno_investment_team;"
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -d agno_investment_team -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### "psql: The term 'psql' is not recognized"
```powershell
# Add PostgreSQL to PATH temporarily for this session
$env:Path += ";C:\Program Files\PostgreSQL\16\bin"

# Now psql should work
psql -U postgres -c "SELECT 1"

# Or use full path
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres -c "SELECT 1"
```

### "Ollama connection error"
```powershell
# Start Ollama if not running
ollama serve

# In another terminal, verify it's listening
netstat -ano | findstr "11434"

# Verify models are pulled
ollama list | findstr "llama3.2|nomic-embed-text"

# Pull missing models
ollama pull llama3.2
ollama pull nomic-embed-text
```

### "EXA_API_KEY not found"
```powershell
# Verify .env file exists and has the key
cat .env | findstr "EXA_API_KEY"

# Test if it's being loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('EXA_API_KEY'))"

# Get free key at https://exa.ai/api
```

### "Port 8000 already in use"
```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 8000 | Select OwningProcess

# Get the process name
Get-Process -Id <PID>

# Kill it
Stop-Process -Id <PID> -Force

# Or run on different port
$env:PORT=8001; python -m app.main
```

---

# Project Structure

```
agno-investment-team/
├── agents/                    # 7 specialist agents
│   ├── market_analyst.py
│   ├── financial_analyst.py
│   ├── technical_analyst.py
│   ├── risk_officer.py
│   ├── knowledge_agent.py
│   ├── memo_writer.py
│   ├── committee_chair.py
│   └── settings.py
│
├── teams/                     # 4 team architectures
│   ├── coordinate_team.py
│   ├── route_team.py
│   ├── broadcast_team.py
│   └── task_team.py
│
├── workflows/
│   └── investment_workflow.py
│
├── app/
│   ├── main.py                # API entry (FastAPI)
│   └── load_knowledge.py      # Database init
│
├── db/                        # Database utilities
│   ├── session.py
│   ├── url.py
│   └── __init__.py
│
├── context/                   # Fund policy docs
│   ├── mandate.md
│   ├── risk_policy.md
│   └── process.md
│
├── research/                  # Company + sector RAG docs
│   ├── companies/
│   └── sectors/
│
├── memos/                     # Past investment decisions
│
├── .env                       # YOUR configuration
├── requirements.txt
├── pyproject.toml
├── compose.yaml               # Docker (Method 1 only)
└── how_to_use.md             # This file
```

---

# Common Workflows

## Development Cycle

```powershell
# Format and validate code
./scripts/format.sh
./scripts/validate.sh

# Rebuild containers with changes
docker compose up -d --build

# Reload knowledge base if you edited research documents
docker exec -it investment-team-api python -m app.load_knowledge --recreate
```

## Adding New Research Documents

```powershell
# 1. Add .md file to research/companies/ or research/sectors/

# 2. Reload knowledge base
python -m app.load_knowledge --recreate

# 3. Test by querying the Knowledge Agent
# "What do you know about [company/sector]?"
```

## Modifying Fund Rules

```powershell
# 1. Edit context/*.md
#    - mandate.md: Portfolio size, limits
#    - risk_policy.md: Position sizing
#    - process.md: Decision framework

# 2. Restart API (changes load automatically)
python -m app.main
```

---

# Useful Commands Reference

## Activation & Deactivation (venv only)

```powershell
# Activate
.\venv_agno_investment_team\Scripts\Activate.ps1

# Deactivate
deactivate
```

## API Control

```powershell
# Start API (venv)
python -m app.main

# Start API on custom port (venv)
$env:PORT=8001; python -m app.main

# Start API (Docker)
docker compose up -d investment-team-api

# View API logs (Docker)
docker logs -f investment-team-api
```

## Database Operations

```powershell
# Reload knowledge base (venv)
python -m app.load_knowledge

# Recreate from scratch (venv)
python -m app.load_knowledge --recreate

# Load research (Docker)
docker exec -it investment-team-api python -m app.load_knowledge

# Connect to PostgreSQL directly (venv)
psql -U postgres -d agno_investment_team

# Connect to PostgreSQL directly (Docker)
docker exec -it investment-team-db psql -U postgres -d agno_investment_team
```

## Code Quality

```powershell
# Format code
./scripts/format.sh

# Validate syntax
./scripts/validate.sh

# Type checking
mypy agents teams workflows app
```

---

# Support & Resources

- **Agno Docs**: https://docs.agno.com
- **Agno GitHub**: https://github.com/agno-agi/agno
- **Agno Discord**: https://agno.com/discord
- **Exa API**: https://docs.exa.ai
- **YFinance**: https://github.com/ranaroussi/yfinance
- **FastAPI**: https://fastapi.tiangolo.com
- **PostgreSQL**: https://www.postgresql.org/docs/

---

**You're ready!** Choose Method 1 (Docker) or Method 2 (venv) above and follow the Quick Start. 🚀
