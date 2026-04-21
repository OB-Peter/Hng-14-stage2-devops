from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import uuid
import os

app = FastAPI()

# BUG 2 & 3 FIX: Use env vars for Redis host and password
r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    password=os.environ.get("REDIS_PASSWORD", None),
    decode_responses=True
)

class JobRequest(BaseModel):
    payload: str = ""

# BUG 12 FIX: Add health endpoint
@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {e}")

# BUG 14 FIX: Accept a payload in the request body
@app.post("/jobs")
def create_job(request: JobRequest):
    job_id = str(uuid.uuid4())
    # BUG 4 FIX: consistent queue name, lpush is fine with brpop
    r.lpush("jobs", job_id)
    r.hset(f"job:{job_id}", mapping={
        "status": "queued",
        "payload": request.payload
    })
    return {"job_id": job_id, "status": "queued"}

# BUG 16 FIX: Return proper 404
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status}