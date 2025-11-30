FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code applicatif
COPY . .

# Flask sera lancé via FLASK_APP depuis .env.backend
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
