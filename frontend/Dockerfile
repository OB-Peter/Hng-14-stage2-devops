# syntax=docker/dockerfile:1

# ── Stage 1: Builder ──────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./

RUN npm ci --omit=dev


# ── Stage 2: Production ───────────────────────────────────────────
FROM node:20-alpine AS production

RUN addgroup --gid 1001 appgroup \
    && adduser \
       --uid 1001 \
       --ingroup appgroup \
       --disabled-password \
       --no-create-home \
       appuser

WORKDIR /app

COPY --from=builder /build/node_modules ./node_modules
COPY --chown=appuser:appgroup app.js package.json ./
COPY --chown=appuser:appgroup views/ ./views/

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider \
    http://localhost:3000/health || exit 1

CMD ["node", "app.js"]
