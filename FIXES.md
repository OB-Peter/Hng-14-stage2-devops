# FIXES.md — Bug Report

All bugs found in the starter repository and how they were fixed.

---

## Fix 1
- **File:** `api/.env`
- **Line:** 1
- **Problem:** `.env` file containing real credentials (`REDIS_PASSWORD=supersecretpassword123`) was committed to the git repository and is now permanent in git history
- **Fix:** Removed from git tracking with `git rm --cached api/.env`, added `.env` to `.gitignore`, created `.env.example` with placeholder values

---

## Fix 2
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis connection hardcoded to `localhost` — fails inside Docker where Redis is a separate container reachable only by service name
- **Fix:** Changed to `os.environ.get("REDIS_HOST", "redis")` to read from environment variable

---

## Fix 3
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis password defined in `.env` but never passed to the Redis connection
- **Fix:** Added `password=os.environ.get("REDIS_PASSWORD", None)` to Redis connection

---

## Fix 4
- **File:** `api/main.py`
- **Line:** 18
- **Problem:** `return {"error": "not found"}` returns HTTP 200 with error in body — clients cannot detect this as a failure
- **Fix:** Changed to `raise HTTPException(status_code=404, detail="Job not found")`

---

## Fix 5
- **File:** `api/main.py`
- **Line:** 4
- **Problem:** `import os` present but never used — env vars were intended but never implemented
- **Fix:** Used `os.environ.get()` for all configuration values

---

## Fix 6
- **File:** `api/main.py`
- **Line:** N/A
- **Problem:** No `/health` endpoint — Docker HEALTHCHECK cannot verify API readiness
- **Fix:** Added `GET /health` endpoint that pings Redis and returns 200 or 503

---

## Fix 7
- **File:** `api/requirements.txt`
- **Line:** 1-3
- **Problem:** No version pins on any dependency — non-deterministic builds
- **Fix:** Pinned all versions: `fastapi==0.115.0`, `uvicorn[standard]==0.30.1`, `redis==5.0.4`, `pydantic==2.9.2`

---

## Fix 8
- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Redis connection hardcoded to `localhost` — fails inside Docker network
- **Fix:** Changed to `os.environ.get("REDIS_HOST", "redis")`

---

## Fix 9
- **File:** `worker/worker.py`
- **Line:** 5
- **Problem:** Redis password never passed to worker Redis connection
- **Fix:** Added `password=os.environ.get("REDIS_PASSWORD", None)`

---

## Fix 10
- **File:** `worker/worker.py`
- **Line:** 12
- **Problem:** `while True` loop with no signal handling — SIGTERM ignored, jobs lost on shutdown
- **Fix:** Added `signal.signal(SIGTERM, handle_shutdown)` and a `running` flag

---

## Fix 11
- **File:** `worker/worker.py`
- **Line:** 14
- **Problem:** No error handling around job processing — any exception crashes worker permanently
- **Fix:** Wrapped in `try/except`, sets job status to `failed` on exception

---

## Fix 12
- **File:** `worker/worker.py`
- **Line:** N/A
- **Problem:** No retry logic for Redis connection at startup — crashes if Redis not ready
- **Fix:** Added retry loop with 10 attempts and 3 second delay

---

## Fix 13
- **File:** `worker/requirements.txt`
- **Line:** 1
- **Problem:** Only `redis` with no version pin
- **Fix:** Pinned to `redis==5.0.4`

---

## Fix 14
- **File:** `frontend/app.js`
- **Line:** 6
- **Problem:** `const API_URL = "http://localhost:8000"` — localhost unreachable from inside container
- **Fix:** Changed to `const API_URL = process.env.API_URL || "http://api:8000"`

---

## Fix 15
- **File:** `frontend/app.js`
- **Line:** 11
- **Problem:** POST to API sends no request body — jobs carry no data
- **Fix:** Pass `req.body` through to the API

---

## Fix 16
- **File:** `frontend/app.js`
- **Line:** N/A
- **Problem:** No `/health` endpoint — Docker HEALTHCHECK cannot verify frontend readiness
- **Fix:** Added `GET /health` returning `{"status": "ok"}`

---

## Fix 17
- **File:** `frontend/views/index.html`
- **Line:** 32
- **Problem:** fetch POST sends no Content-Type header and no body — payload always lost
- **Fix:** Added `Content-Type: application/json` header and JSON body

---

## Fix 18
- **File:** `frontend/package.json`
- **Line:** N/A
- **Problem:** No `package-lock.json` — `npm ci` cannot run without a lockfile
- **Fix:** Generated `package-lock.json` with `npm install` and committed it

---

## Fix 19
- **File:** `docker-compose.yml`
- **Line:** N/A
- **Problem:** No `docker-compose.yml` provided in starter repo
- **Fix:** Created complete `docker-compose.yml` with named networks, health checks, resource limits, and proper dependency ordering
