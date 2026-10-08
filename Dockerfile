# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Prevent Python from writing .pyc files, enable unbuffered logging and configure Berlin timezone
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=Europe/Berlin

WORKDIR /app

# Install security certificates, tzdata (Europe/Berlin timezone) & minimal runtime requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && echo "Europe/Berlin" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Create non-root system user and group
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -s /bin/bash -m appuser

# Install Python production dependencies first for optimal Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY --chown=appuser:appuser . .

# Ensure data directory exists with non-root ownership
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# Mount point for flat-file Markdown store and sync cache
VOLUME ["/app/data"]

# Default entrypoint allows invoking any pipeline runner directly:
# e.g.: docker run p2p-news p2p_news_scraper.py --provider nectaro
#       docker run p2p-news pipeline_orchestrator.py
ENTRYPOINT ["python"]
CMD ["p2p_news_scraper.py", "--help"]
