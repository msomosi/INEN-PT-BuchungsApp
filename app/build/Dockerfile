FROM python:3-slim AS base

ARG module
WORKDIR /app

# Systempakete für psycopg2 installieren
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY build/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


FROM base
COPY ${module} .
COPY build/factory.py .
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "app:app"]
