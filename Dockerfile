# ---------- Build Stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed to build Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in build stage
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn whitenoise

# Copy project code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# ---------- Production Stage ----------
FROM python:3.11-slim AS production

WORKDIR /app

# Copy installed dependencies and collected static files from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

# Expose the port the app runs on
EXPOSE 8000

# Set entrypoint to handle migrations at container runtime
ENTRYPOINT ["sh", "-c"]
CMD ["python manage.py migrate && gunicorn core.wsgi:application --bind 0.0.0.0:8000"]
