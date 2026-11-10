# Week 9: System Integration, Containerization & Cloud Deployment

**Project:** Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts  
**Scope:** Complete multi-week integration (Weeks 1 through 9), Docker containerization, production API server, and cloud deployment readiness.  

---

## 1. Unified Pipeline Architecture

Week 9 integrates all scientific modules, data processing steps, machine-learning models, explainability engines, and alerting systems into a single reproducible pipeline runner: `src/run_pipeline.py`.

### 1.1 Complete Pipeline Execution Flow
```
[1/18] GFS Download (0.25° medium-range forecasts)
  │
[2/18] ERA5 Download (0.25° reanalysis reference ground truth)
  │
[3/18] Preprocessing & Spatial/Temporal Standardization
  │
[4/18] Data Quality Verification & Physical Bounds Screening
  │
[5/18] Temporal Feature Extraction (Rolling Means & Departures)
  │
[6/18] Statistical Anomaly Detection (Z-Score & Robust MAD)
  │
[7/18] Baseline Validation (GFS vs. ERA5 verification)
  │
[8/18] Week 3: Multi-Horizon Error Analysis & Bias Correction
  │
[9/18] Week 4: Spatiotemporal Reliability Scoring (R = R_error × C)
  │
[10/18] Week 5: Machine-Learning Forecast-Bust Classifier Training
  │
[11/18] Week 1 & 2 Visualizations (Time Series, Correlations)
  │
[12/18] Week 3 Visualizations (Error Curves, Bias Distributions)
  │
[13/18] Week 4 Visualizations (Reliability Curves, Spatiotemporal Heatmap)
  │
[14/18] Week 5 Visualizations (PR Curves, Confusion Matrix, Feature Importance)
  │
[15/18] Week 7: SHAP Feature Influence Analysis & High-Error Attributions
  │
[16/18] Week 8: Regional Reliability & Uncertainty Analysis (1 to 10 Days)
  │
[17/18] Week 8: Automated Forecast-Bust Alert Generation & Storage
  │
[18/18] Week 9: System Integration & Integrity Health Check
```

### 1.2 Pipeline Execution Commands
```bash
# Execute complete end-to-end pipeline
./.venv/bin/python src/run_pipeline.py --stage all

# Execute specific week stages
./.venv/bin/python src/run_pipeline.py --stage week8
./.venv/bin/python src/run_pipeline.py --stage week9
./.venv/bin/python src/run_pipeline.py --stage explainability

# Fast test execution (reusing local datasets without network downloading)
./.venv/bin/python src/run_pipeline.py --test --skip-download
```

---

## 2. Docker Containerization Architecture

The system is containerized as a decoupled two-tier microservices architecture:
1. **Python FastAPI Backend Service (`backend`):** Hosts the REST API, ML inference engine, SHAP explainer, LangChain agent, and automated alerting engine.
2. **React/Vite Frontend Service (`frontend`):** Pre-compiled production Single Page Application served by an optimized Nginx web server with built-in reverse proxying.

### 2.1 Backend Container (`Dockerfile`)
- **Base Image:** `python:3.11-slim` (minimal footprint, fast vulnerability scanning).
- **Security:** Runs as non-root user `appuser` (UID 1001).
- **Environment:** `PYTHONUNBUFFERED=1`, `MPLCONFIGDIR=/tmp/matplotlib`.
- **Health Check:** `curl -f http://localhost:8000/api/health || exit 1`.
- **Volume Mounts:**
  - `/app/data`: Persistent meteorological datasets and geographical boundaries.
  - `/app/outputs`: Persistent model weights, SHAP figures, and alerts database.

### 2.2 Frontend Container (`frontend/Dockerfile`)
- **Multi-Stage Build:**
  - Stage 1 (Builder): `node:20-alpine` runs `npm ci` and `npm run build`.
  - Stage 2 (Runtime): `nginx:alpine` copies `/app/dist` to `/usr/share/nginx/html`.
- **Nginx Reverse Proxy:** Routes all `/api/*` traffic transparently to `http://backend:8000/api/` inside the Docker bridge network.
- **SPA Fallback:** Implements `try_files $uri $uri/ /index.html;` for seamless client-side routing.

### 2.3 Docker Compose Orchestration (`docker-compose.yml`)
```yaml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 15s
      timeout: 5s
      retries: 3
  frontend:
    build: ./frontend
    ports: ["80:80", "5173:80"]
    depends_on:
      backend:
        condition: service_healthy
```

---

## 3. Cloud Deployment Strategy

### 3.1 Recommended Deployment Platforms

| Platform | Recommended Plan | Persistence | Configuration Ease | Suitability |
| :--- | :--- | :---: | :---: | :--- |
| **Render** | Web Service (Docker) + Disk | ✅ Persistent Disk | High | **Recommended for PaaS** |
| **Railway** | Dockerfile Service + Volume | ✅ Volume Mount | High | **Recommended for PaaS** |
| **AWS / GCP VM** | EC2 / Compute Engine (Ubuntu) | ✅ EBS / Persistent Disk | Moderate | **Recommended for Full Control** |
| **AWS ECS / GCP Cloud Run**| Container Serverless + S3/GCS | ✅ Cloud Object Storage | Advanced | Scalable enterprise |

### 3.2 Production Deployment Procedure (Docker on Linux VM / Cloud VPS)
```bash
# 1. Clone repository on target server
git clone https://github.com/Akshit029/minor-project.git
cd minor-project

# 2. Configure production environment
cp .env.example .env
nano .env   # Set ALERT_THRESHOLD, optional GEMINI_API_KEY, SMTP settings

# 3. Build and launch services in detached mode
docker compose up -d --build

# 4. Verify container health status
docker compose ps
curl -f http://localhost:8000/api/health

# 5. Inspect application logs
docker compose logs -f backend
```

---

## 4. End-to-End Testing and Verification

The test suite validates the full data-to-alert operational chain across 91 automated tests:
```bash
# Run full pytest suite (Weeks 1 through 9)
./.venv/bin/pytest

# Run Week 9 integration tests specifically
./.venv/bin/pytest tests/test_week9_pipeline.py
```
- **Test Results:** 91 passed in 3.79s (100% success rate, 0 warnings, 0 regressions).

