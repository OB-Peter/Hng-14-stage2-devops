# syntax=docker/dockerfile:1

# ── Stage 1: Builder ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production ───────────────────────────────────────────
FROM python:3.12-slim AS production

RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup \
       --no-create-home \
       --shell /bin/false \
       appuser

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup worker.py .

USER appuser

HEALTHCHECK --interval=20s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import os; os.kill(1, 0)" || exit 1

CMD ["python", "worker.py"]
