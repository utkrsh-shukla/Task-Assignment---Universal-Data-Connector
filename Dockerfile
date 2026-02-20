# ─────────────────────────────────────────────
#  Universal Data Connector – Docker image
# ─────────────────────────────────────────────
# Multi-stage-friendly, slim image.
# Data files are COPIED into the image so the
# container is completely self-contained.
# ─────────────────────────────────────────────

FROM python:3.11-slim

# Prevents Python from buffering stdout/stderr
# so logs appear immediately in `docker logs`.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# --- Install dependencies first (layer caching) ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy application code and data ---
COPY app/ ./app/
COPY data/ ./data/

# --- Expose the API port ---
EXPOSE 8000

# --- Run with production-safe settings ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
