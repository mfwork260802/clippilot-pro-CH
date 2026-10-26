# Clipper Hub Cheat Pro: React + Vite frontend, FastAPI + FFmpeg backend

# Stage 1: build the frontend
FROM node:22-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY index.html vite.config.ts tsconfig*.json eslint.config.js ./
COPY public ./public
COPY src ./src
RUN npm run build

# Stage 2: runtime
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    DATA_DIR=/data \
    WHISPER_MODEL=small \
    WHISPER_DOWNLOAD_ROOT=/models
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg libgl1 libglib2.0-0 curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# Bake the Whisper model into the image so the first render does not wait for a download
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('${WHISPER_MODEL}', device='cpu', compute_type='int8', download_root='${WHISPER_DOWNLOAD_ROOT}')"

COPY backend ./backend
COPY --from=frontend /app/dist ./dist
RUN mkdir -p /data

EXPOSE 8000
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]
