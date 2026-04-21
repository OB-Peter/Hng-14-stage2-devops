# Job Processing System — DevOps Stage 2

> A production-ready, fully containerized microservices application built as part of the **HNG14 DevOps Track Stage 2** assessment. The system demonstrates real-world DevOps practices including multi-stage Docker builds, health-checked service orchestration, and a complete six-stage CI/CD pipeline.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Services](#services)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests Locally](#running-tests-locally)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)

---

## Overview

This project is a production-ready, fully containerized microservices application built for the HNG14 DevOps Track Stage 2 assessment. It demonstrates real-world DevOps practices including multi-stage Docker builds, health-checked service orchestration, and a complete six-stage CI/CD pipeline.

> **Note:** All services communicate over a named internal Docker network. Redis is never exposed to the host machine. Each service has a health check and only starts after its dependencies are confirmed healthy.

---

## Architecture

```
                ┌─────────────────────────────────────┐
                │         job_processing_network       │
                │                                     │
  [Browser] ────► [Frontend :3000] ──────► [API :8000] │
                │                   │                 │
                │               [Redis]               │
                │                   ▲                 │
                │               [Worker]              │
                └─────────────────────────────────────┘
```

---

## Services

| Service  | Technology       | Port | Description                                       |
|----------|------------------|------|---------------------------------------------------|
| Frontend | Node.js/Express  | 3000 | Web UI for submitting jobs and tracking status    |
| API      | Python/FastAPI   | 8000 | Creates jobs, serves status, exposes health check |
| Worker   | Python           | —    | Picks up jobs from Redis queue and processes them |
| Redis    | Redis 7.2        | 6379 | Message queue shared between API and Worker       |

---

## Prerequisites

Ensure the following are installed on your machine before starting. No cloud account, paid service, or extra configuration is needed beyond what is documented here.

| Tool           | Minimum Version | Check Command            |
|----------------|-----------------|--------------------------|
| Docker         | 24.x            | `docker --version`       |
| Docker Compose | v2.24           | `docker compose version` |
| Git            | 2.x             | `git --version`          |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/hng14-stage2-devops
cd hng14-stage2-devops
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` in any editor and set your `REDIS_PASSWORD` to a strong value. All other defaults work out of the box for local development.

```bash
# Minimum required change
REDIS_PASSWORD=your_strong_password_here
```

> ⚠️ **Never commit your `.env` file** — it is blocked by `.gitignore`.

### 3. Build and Start the Full Stack

```bash
docker compose up --build -d
```

This command will:

- Build all three service images from source
- Pull the official Redis 7.2 image
- Start all four containers in the correct dependency order
- Run health checks to confirm each service is ready

### 4. Confirm All Services Are Healthy

```bash
docker compose ps
```

Wait up to 90 seconds for all services to initialise. A successful startup looks exactly like this:

```
NAME       IMAGE                 COMMAND                  STATUS
redis      redis:7.2-alpine      docker-entrypoint.s...   Up 2 minutes (healthy)
api        job-api:latest        uvicorn main:app ...     Up 2 minutes (healthy)
worker     job-worker:latest     python worker.py         Up 2 minutes (healthy)
frontend   job-frontend:latest   docker-entrypoint.s...   Up 1 minute  (healthy)
```

> All four services must show `(healthy)` before proceeding. If any service shows `(unhealthy)` or `(starting)`, wait a further 30 seconds and run `docker compose ps` again.

### 5. Open the Application

Visit **http://localhost:3000** in your browser.

- You will see the **Job Processor Dashboard**
- Click **Submit New Job** to create a job
- The job status will automatically update: `queued` → `processing` → `completed`

### 6. Verify End-to-End via the Terminal

```bash
# Submit a job
RESPONSE=$(curl -sf -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{"payload": "hello-world"}')

echo "Submitted: $RESPONSE"

# Extract the job ID
JOB_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

# Wait for the worker to process it
sleep 5

# Check the final status — should be "completed"
curl -s http://localhost:3000/status/$JOB_ID
```

Expected final response:

```json
{"job_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "status": "completed"}
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values. Never commit your `.env` file.

| Variable              | Description                               | Default          |
|-----------------------|-------------------------------------------|------------------|
| `REDIS_PASSWORD`      | Password for Redis authentication         | *(required)*     |
| `REDIS_HOST`          | Redis hostname inside Docker network      | `redis`          |
| `REDIS_PORT`          | Redis port                                | `6379`           |
| `API_URL`             | API base URL used by the frontend         | `http://api:8000`|
| `FRONTEND_PORT`       | Host machine port for the frontend        | `3000`           |
| `REDIS_CPU_LIMIT`     | CPU limit for Redis container             | `0.50`           |
| `REDIS_MEMORY_LIMIT`  | Memory limit for Redis container          | `128M`           |
| `API_CPU_LIMIT`       | CPU limit for API container               | `1.00`           |
| `API_MEMORY_LIMIT`    | Memory limit for API container            | `256M`           |
| `WORKER_CPU_LIMIT`    | CPU limit for Worker container            | `1.00`           |
| `WORKER_MEMORY_LIMIT` | Memory limit for Worker container         | `128M`           |
| `FRONTEND_CPU_LIMIT`  | CPU limit for Frontend container          | `0.50`           |
| `FRONTEND_MEMORY_LIMIT` | Memory limit for Frontend container     | `128M`           |

---

## API Reference

The API is available at **http://localhost:8000**

### Health Check

```
GET /health
```

Returns `200` if the API is running and Redis is reachable. Returns `503` if Redis is unavailable.

```bash
curl http://localhost:8000/health
```

```json
{"status": "ok"}
```

---

### Create a Job

```
POST /jobs
```

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"payload": "my-job-data"}'
```

```json
{
  "job_id": "d9010275-7636-46c6-a3e1-b64920d668de",
  "status": "queued"
}
```

---

### Get Job Status

```
GET /jobs/{job_id}
```

```bash
curl http://localhost:8000/jobs/d9010275-7636-46c6-a3e1-b64920d668de
```

```json
{
  "job_id": "d9010275-7636-46c6-a3e1-b64920d668de",
  "status": "completed"
}
```

---

### Job Status Values

| Status       | Meaning                                                  |
|--------------|----------------------------------------------------------|
| `queued`     | Job received and waiting to be picked up by the worker   |
| `processing` | Worker has picked up the job and is actively running     |
| `completed`  | Job finished successfully                                |
| `failed`     | Job encountered an error during processing               |

---

## Running Tests Locally

Unit tests run against a fully mocked Redis instance — no running containers required.

```bash
cd api

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install all dependencies including test requirements
pip install -r requirements.txt -r tests/requirements-test.txt

# Run all tests with coverage report
python -m pytest tests/ -v --cov=main --cov-report=term-missing

# Deactivate when done
deactivate
cd ..
```

Expected output:

```
tests/test_api.py::test_health_returns_ok                           PASSED
tests/test_api.py::test_health_returns_503_when_redis_down          PASSED
tests/test_api.py::test_create_job_returns_job_id_and_queued_status PASSED
tests/test_api.py::test_create_job_pushes_to_redis_queue            PASSED
tests/test_api.py::test_create_job_stores_status_in_redis           PASSED
tests/test_api.py::test_get_job_returns_correct_status              PASSED
tests/test_api.py::test_get_job_returns_404_when_not_found          PASSED

7 passed  |  Coverage: 100%
```

---

## CI/CD Pipeline

The pipeline is defined in `.github/workflows/ci-cd.yml` and runs automatically on every push. A failure in any stage immediately stops all subsequent stages from running.

### Pipeline Overview

```
Stage 1      Stage 2     Stage 3     Stage 4       Stage 5          Stage 6
  Lint   ──►  Test  ──►  Build  ──►  Security  ──►  Integration  ──►  Deploy
                                       Scan              Test
```

### Stage Details

#### Stage 1 — Lint

Checks code quality across all three languages and all Dockerfiles.

- **Python:** `flake8` with max line length 100
- **JavaScript:** ESLint with zero warnings allowed
- **Dockerfiles:** `hadolint` on all three Dockerfiles

#### Stage 2 — Unit Tests

Runs the API test suite with Redis fully mocked.

- 7 unit tests covering all endpoints
- Coverage report generated and uploaded as a pipeline artifact
- Pipeline fails if coverage drops below 80%

#### Stage 3 — Build

Builds all three Docker images using Docker Buildx and pushes them to a local registry running as a service container inside the CI job.

- Each image is tagged with the full git SHA and `latest`
- Multi-stage builds ensure production images contain no build tools
- Build cache is shared across runs for speed

#### Stage 4 — Security Scan

Scans all three images with [Trivy](https://github.com/aquasecurity/trivy).

- Pipeline fails immediately on any `CRITICAL` severity CVE
- Scan results are uploaded as SARIF artifacts
- Results are available in the Actions run artifacts tab

#### Stage 5 — Integration Test

Brings the full four-service stack up inside the GitHub Actions runner.

- Waits for all services to pass their health checks
- Submits a real job through the frontend HTTP endpoint
- Polls the status endpoint until the job reaches `completed`
- Tears the stack down cleanly regardless of outcome

#### Stage 6 — Deploy

Runs only on pushes to the `main` branch. Performs a scripted rolling update over SSH.

- New container starts alongside the old one
- New container must pass its health check within 60 seconds
- If health check passes, old container is stopped and removed
- If health check fails within 60 seconds, old container is kept running and the deploy aborts

> ⚠️ Requires `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, and `DEPLOY_USER` GitHub Secrets to be configured in the repository settings.

---

## Project Structure

```
hng14-stage2-devops/
├── .github/
│   └── workflows/
│       └── ci-cd.yml            # Six-stage CI/CD pipeline
├── api/
│   ├── Dockerfile               # Multi-stage production Dockerfile
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Pinned Python dependencies
│   └── tests/
│       ├── __init__.py
│       ├── requirements-test.txt
│       └── test_api.py          # 7 unit tests with mocked Redis
├── worker/
│   ├── Dockerfile               # Multi-stage production Dockerfile
│   ├── worker.py                # Redis queue consumer
│   └── requirements.txt         # Pinned Python dependencies
├── frontend/
│   ├── Dockerfile               # Multi-stage production Dockerfile
│   ├── app.js                   # Express server
│   ├── package.json
│   ├── package-lock.json
│   ├── eslint.config.cjs        # ESLint configuration
│   └── views/
│       └── index.html           # Job dashboard UI
├── docker-compose.yml           # Full stack orchestration
├── .dockerignore                # Prevents secrets entering images
├── .env.example                 # Template for environment variables
├── .gitignore                   # Ensures .env is never committed
├── .hadolint.yaml               # Hadolint configuration
├── FIXES.md                     # All bugs found and fixed
└── README.md                    # This file
```

---

## Troubleshooting

### One or More Services Show Unhealthy

```bash
# Check logs for the unhealthy service
docker compose logs api
docker compose logs worker
docker compose logs redis
docker compose logs frontend
```

### See Exactly What a Health Check Is Returning

```bash
docker inspect api --format '{{json .State.Health.Log}}' | python3 -m json.tool
docker inspect worker --format '{{json .State.Health.Log}}' | python3 -m json.tool
```

### Frontend Returns Error When Submitting a Job

```bash
# Confirm the API is reachable from inside the frontend container
docker exec frontend wget -qO- http://api:8000/health
```

### Redis Authentication Errors in API or Worker Logs

Verify `REDIS_PASSWORD` is identical in your `.env` for all services. The Redis container and both application containers must use the same password.

### Jobs Stay in `queued` Status and Never Complete

The worker is not processing jobs. Check:

```bash
docker compose logs worker

# If the worker shows Redis connection errors, confirm Redis is healthy:
docker compose ps redis
```

### Stop the Stack

```bash
# Stop all containers
docker compose down

# Stop all containers and remove Redis data volume
docker compose down -v

# Stop and remove all built images as well
docker compose down -v --rmi all
```

---

## Security Notes

- The `.env` file is blocked from git by `.gitignore` — never override this
- No secrets, credentials, or `.env` files are copied into any Docker image
- All containers run as a non-root user (`appuser`, UID 1001)
- Redis is not exposed on the host machine — only reachable inside the Docker network
- All images are scanned for `CRITICAL` CVEs before deployment

---

*Job Processing System · HNG14 DevOps Track Stage 2 · Production-Ready Microservices*