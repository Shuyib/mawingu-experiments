FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate sample data
RUN python scripts/generate_sample_data.py && \
    python scripts/load_sample_data.py

# Run dbt models
WORKDIR /app/dbt_project
RUN dbt deps && \
    dbt run && \
    dbt test

# Back to app directory
WORKDIR /app

# Expose Dagster webserver port
EXPOSE 3000

# Start Dagster webserver
CMD ["dagster", "dev", "-f", "orchestrator/dagster_pipeline.py", "-h", "0.0.0.0", "-p", "3000"]
