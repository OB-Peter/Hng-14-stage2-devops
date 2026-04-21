#!/usr/bin/env bash
set -euo pipefail

echo "=== Starting Integration Test ==="

# Start the stack
docker compose up -d

echo "Waiting for all services to be healthy..."
timeout 120 bash -c '
  until \
    [ "$(docker inspect --format={{.State.Health.Status}} api 2>/dev/null)" = "healthy" ] && \
    [ "$(docker inspect --format={{.State.Health.Status}} frontend 2>/dev/null)" = "healthy" ] && \
    [ "$(docker inspect --format={{.State.Health.Status}} worker 2>/dev/null)" = "healthy" ] && \
    [ "$(docker inspect --format={{.State.Health.Status}} redis 2>/dev/null)" = "healthy" ]; do
    echo "Services not all healthy yet..."
    docker compose ps
    sleep 5
  done
'
echo "All services healthy!"

echo "=== Submitting job ==="
RESPONSE=$(curl -sf \
  -X POST http://localhost:3000/submit \
  -H "Content-Type: application/json" \
  -d '{"payload":"integration-test"}')

echo "Response: $RESPONSE"

JOB_ID=$(echo "$RESPONSE" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"

echo "=== Polling for completion ==="
MAX=30
COUNT=0

while [ $COUNT -lt $MAX ]; do
  STATUS=$(curl -sf "http://localhost:3000/status/${JOB_ID}" | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['status'])")

  echo "Attempt $COUNT: status = $STATUS"

  if [ "$STATUS" = "completed" ]; then
    echo "✅ Integration test PASSED — job completed successfully"
    docker compose down -v --remove-orphans
    exit 0
  fi

  if [ "$STATUS" = "failed" ]; then
    echo "❌ Integration test FAILED — job status is failed"
    docker compose down -v --remove-orphans
    exit 1
  fi

  COUNT=$((COUNT + 1))
  sleep 3
done

echo "❌ Integration test FAILED — timed out after $((MAX * 3)) seconds"
docker compose down -v --remove-orphans
exit 1
