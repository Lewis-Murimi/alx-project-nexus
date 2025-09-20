# Dockerfile
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN pip install gunicorn

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]