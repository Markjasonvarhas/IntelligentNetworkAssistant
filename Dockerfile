# ==============================================================================
# STAGE 1: Build Vue 3 Frontend
# ==============================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# ==============================================================================
# STAGE 2: Python Backend & Production Runtime
# ==============================================================================
FROM python:3.11-slim

# Install system dependencies including Linux ping (iputils-ping) and curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    iproute2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy Backend Source Code & Datasets
COPY backend/ ./backend/

# Copy Compiled Vue 3 Frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Train ML model inside the container on build
RUN python backend/model/train_model.py

# Set environment variables
ENV PORT=10000
ENV PYTHONUNBUFFERED=1

EXPOSE 10000

# Start Production Web Server with Gunicorn (binds dynamically to Render's $PORT)
CMD ["sh", "-c", "gunicorn --chdir backend --bind 0.0.0.0:${PORT:-10000} --workers 2 --threads 4 --timeout 120 app:app"]
