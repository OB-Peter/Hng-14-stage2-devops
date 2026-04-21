"""
Unit tests for the Job Processing API.
Redis is fully mocked — no real Redis needed.
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# ── Mock Redis before importing app ──────────────────────────────────────────
@pytest.fixture(autouse=True)
def mock_redis():
    """Replace the redis.Redis instance in main.py with a mock."""
    with patch("main.r") as mock_r:
        yield mock_r


@pytest.fixture
def client(mock_redis):
    from main import app
    return TestClient(app)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_health_returns_ok(client, mock_redis):
    """Health endpoint returns 200 and status ok when Redis responds."""
    mock_redis.ping.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_returns_503_when_redis_down(client, mock_redis):
    """Health endpoint returns 503 when Redis is unreachable."""
    mock_redis.ping.side_effect = Exception("Connection refused")

    response = client.get("/health")

    assert response.status_code == 503


def test_create_job_returns_job_id_and_queued_status(client, mock_redis):
    """POST /jobs returns a job_id and status=queued."""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post("/jobs", json={"payload": "test-payload"})

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    # job_id must be a valid UUID (36 chars with dashes)
    assert len(data["job_id"]) == 36


def test_create_job_pushes_to_redis_queue(client, mock_redis):
    """POST /jobs must call lpush to enqueue the job."""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    client.post("/jobs", json={"payload": "test-payload"})

    # Verify job was pushed to the queue
    mock_redis.lpush.assert_called_once()
    call_args = mock_redis.lpush.call_args[0]
    assert call_args[0] == "jobs"  # correct queue name


def test_create_job_stores_status_in_redis(client, mock_redis):
    """POST /jobs must store the job status in Redis as queued."""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    client.post("/jobs", json={"payload": "test-payload"})

    # Verify hset was called to store job status
    mock_redis.hset.assert_called_once()
    call_kwargs = mock_redis.hset.call_args[1]
    assert call_kwargs["mapping"]["status"] == "queued"


def test_get_job_returns_correct_status(client, mock_redis):
    """GET /jobs/{id} returns the job status from Redis."""
    mock_redis.hget.return_value = "completed"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "some-job-id"
    assert data["status"] == "completed"


def test_get_job_returns_404_when_not_found(client, mock_redis):
    """GET /jobs/{id} returns 404 when job does not exist."""
    mock_redis.hget.return_value = None

    response = client.get("/jobs/nonexistent-id")

    assert response.status_code == 404
