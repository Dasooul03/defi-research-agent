# Stage 1: Build frontend static files
FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY frontend/package.json ./

RUN npm config set registry https://registry.npmmirror.com && \
    npm install && npm cache clean --force

COPY frontend/ .

RUN npm run build

# Stage 2: Python backend + serve frontend static
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/
COPY --from=frontend-builder /app/out ./static

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
