# Use official Python slim image
FROM python:3.11-slim

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.8.5

# Copy only poetry files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no virtualenv, install system-wide)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Create a non-root user
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /umbrella
USER appuser

WORKDIR /umbrella

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
