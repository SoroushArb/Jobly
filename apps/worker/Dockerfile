# Dockerfile for Jobly Worker
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (same as API for LaTeX compilation)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    latexmk \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent context
COPY api/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy worker code
COPY worker/worker.py .
COPY worker/handlers ./handlers

# Copy API code (worker imports from API)
COPY api/app ./api/app
COPY api/job_sources_config.yaml ./api/

# Run the worker
CMD ["python", "worker.py"]
