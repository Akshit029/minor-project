# Production Dockerfile for Weather Forecast Reliability Backend API
FROM python:3.11-slim

# Prevent Python from writing .pyc and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLCONFIGDIR=/tmp/matplotlib

WORKDIR /app

# Install system dependencies (curl for healthcheck, libgomp1 for scikit-learn OpenMP)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and config
COPY config.yaml pytest.ini ./
COPY src/ ./src/
COPY data/ ./data/
COPY outputs/ ./outputs/

# Create non-root user and ensure proper permissions
RUN useradd -m -u 1001 appuser && \
    mkdir -p /tmp/matplotlib outputs/week8 data/geography && \
    chown -R appuser:appuser /app /tmp/matplotlib

USER appuser

EXPOSE 8000

# Operational container health check
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start FastAPI application with Uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]

