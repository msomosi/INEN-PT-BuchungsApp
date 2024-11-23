FROM python:3.8-slim

WORKDIR /app

# Systempakete für psycopg2 installieren
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["python", "app.py"]
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "app:app"]
