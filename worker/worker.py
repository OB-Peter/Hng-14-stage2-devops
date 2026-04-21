import redis
import time
import os
import signal
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

# BUG 5 & 6 FIX: Use env vars for Redis connection
r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    password=os.environ.get("REDIS_PASSWORD", None),
    decode_responses=True
)

# BUG 7 FIX: Graceful shutdown
running = True

def handle_shutdown(signum, frame):
    global running
    logger.info("Shutdown signal received, stopping gracefully...")
    running = False

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

def process_job(job_id):
    logger.info(f"Processing job {job_id}")
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")
    logger.info(f"Done: {job_id}")

# Wait for Redis to be ready
for attempt in range(10):
    try:
        r.ping()
        logger.info("Connected to Redis")
        break
    except redis.ConnectionError:
        logger.warning(f"Redis not ready, attempt {attempt + 1}/10...")
        time.sleep(3)
else:
    logger.error("Could not connect to Redis after 10 attempts")
    sys.exit(1)

logger.info("Worker started, waiting for jobs...")

# BUG 7 & 8 FIX: Proper loop with signal handling and error catching
while running:
    try:
        # BUG 4 FIX: queue name matches api — "jobs"
        job = r.brpop("jobs", timeout=5)
        if job:
            _, job_id = job
            r.hset(f"job:{job_id}", "status", "processing")
            try:
                process_job(job_id)
            except Exception as e:
                # BUG 8 FIX: Don't crash — mark job as failed
                logger.error(f"Job {job_id} failed: {e}")
                r.hset(f"job:{job_id}", "status", "failed")
    except redis.ConnectionError as e:
        logger.error(f"Redis connection lost: {e}, retrying...")
        time.sleep(5)

logger.info("Worker stopped")