# Docker Containerization Guide

This guide details how to build, run, test, and manage the **Weather Forecast Reliability & Uncertainty Detection** application using Docker and Docker Compose.

---

## 1. Prerequisites

- Docker Engine version 20.10+ or Docker Desktop
- Docker Compose v2.0+

Verify your installation:
```bash
docker --version
docker compose version
```

---

## 2. Quickstart with Docker Compose

### Step 1: Prepare Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```
Edit `.env` to configure operational parameters (e.g. `ALERT_THRESHOLD=0.60`, optional `GEMINI_API_KEY`).

### Step 2: Build and Start Services
Launch both the Python backend API and the React/Nginx frontend in detached mode:
```bash
docker compose up -d --build
```

### Step 3: Verify Running Services
```bash
docker compose ps
```
Expected output:
```
NAME                           IMAGE                               COMMAND                  SERVICE    STATUS
weather-reliability-backend    minor-project-backend:latest        "uvicorn src.api:app…"   backend    Up (healthy)
weather-reliability-frontend   minor-project-frontend:latest       "/docker-entrypoint.…"   frontend   Up
```

### Step 4: Access the Application
- **Frontend Dashboard:** [http://localhost:80](http://localhost:80) or [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 3. Container Services Architecture

The application runs as two networked containers on the `weather-net` bridge network:

| Service | Container Name | Port | Description |
| :--- | :--- | :---: | :--- |
| **`backend`** | `weather-reliability-backend` | `8000` | FastAPI server hosting ML models, SHAP explainability, alerting engine, and agentic AI. |
| **`frontend`** | `weather-reliability-frontend` | `80`, `5173` | Production React SPA served via Nginx with reverse proxy to backend `/api/`. |

### Persistent Volume Mounts
The backend service mounts host directories to persist generated artifacts across container restarts:
- `./data:/app/data` — Meteorological netCDF/CSV datasets and geographical boundaries.
- `./outputs:/app/outputs` — Trained model weights, SHAP figures, uncertainty metrics, and active alerts (`outputs/week8/alerts.json`).

---

## 4. Operational Commands

### View Service Logs
```bash
# Follow all logs
docker compose logs -f

# Follow backend logs specifically
docker compose logs -f backend

# Follow frontend access logs
docker compose logs -f frontend
```

### Run Pipeline Stages Inside Container
Execute pipeline analysis inside the running backend container:
```bash
# Run Week 8 automated alerting and uncertainty analysis
docker compose exec backend python src/run_pipeline.py --stage week8

# Run full pipeline
docker compose exec backend python src/run_pipeline.py --stage all
```

### Run Test Suite Inside Container
```bash
docker compose exec backend pytest
```

### Stop Services
```bash
# Stop containers while preserving volume data
docker compose down

# Stop and remove all volumes and orphans
docker compose down -v
```

---

## 5. Standalone Container Builds

If you prefer to run services individually without Docker Compose:

### Build & Run Backend Only
```bash
docker build -t weather-backend .
docker run -d --name weather-backend \
  -p 8000:8000 \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/outputs:/app/outputs" \
  weather-backend
```

### Build & Run Frontend Only
```bash
docker build -t weather-frontend ./frontend
docker run -d --name weather-frontend \
  -p 80:80 \
  weather-frontend
```

---

## 6. Troubleshooting

- **Port Conflict (Port 80 or 8000 already in use):**
  Edit `docker-compose.yml` to remap host ports, e.g. `"8080:80"` or `"8001:8000"`.
- **Health Check Failing:**
  Verify backend logs using `docker compose logs backend`. Ensure required model artifacts in `outputs/week5/` and `outputs/week4/` are present.
- **Permissions Warning:**
  The backend container runs as non-root user `appuser` (UID 1001). Ensure host directories `outputs/` and `data/` are readable and writable.

