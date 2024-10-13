FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["python", "app.py"]
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "app:app"]
