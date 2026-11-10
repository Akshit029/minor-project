# Cloud Deployment & Production Operations Guide

**Project:** Spatiotemporal Reliability and Uncertainty Detection for Medium-Range Weather Forecasts  
**Target Domain:** Jammu and Kashmir  

This guide provides end-to-end instructions for deploying the containerized weather reliability system to production cloud environments.

---

## 1. Architecture & Deployment Overview

The system consists of two production services:
1. **Backend Service (FastAPI / Python 3.11):** High-performance asynchronous API hosting scikit-learn models, SHAP explainability engines, LangChain agent, and alerting workflows. Exposes port `8000`.
2. **Frontend Service (React 19 / Nginx):** Production Single-Page Application served by an Alpine Nginx image with built-in `/api/` reverse proxy and static caching. Exposes port `80`.

```
[Web User / Client Browser]
             │
             ▼ Port 80 / 443
   [Nginx Frontend Container]
             │
             ├── Static assets (/assets/*) ──► Served from /usr/share/nginx/html
             └── Reverse proxy (/api/*)   ──► [FastAPI Backend Container:8000]
                                                        │
                                                        ├── Persistent Volumes:
                                                        │   ├── /app/data (ERA5/GFS netCDF)
                                                        │   └── /app/outputs (Models, Alerts)
                                                        └── LLM API (Google Gemini)
```

---

## 2. Cloud Platform Deployment Options

### Option A: Cloud VM / VPS (Ubuntu 22.04 / 24.04 LTS) — *Recommended for Full Control & Low Cost*
Compatible with DigitalOcean Droplets ($6/mo), Hetzner ($4/mo), AWS EC2 (`t3.medium`), or GCP Compute Engine (`e2-medium`).

#### Step 1: Server Provisioning & Docker Installation
```bash
# Connect to your server
ssh ubuntu@your-server-ip

# Install Docker Engine and Compose plugin
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker ubuntu
```

#### Step 2: Clone Repository & Configure Environment
```bash
git clone https://github.com/Akshit029/minor-project.git
cd minor-project

cp .env.example .env
nano .env
```
Ensure `.env` contains:
```env
ALERT_THRESHOLD=0.60
GEMINI_API_KEY=your_actual_gemini_api_key_here
LLM_MODEL=gemini-2.0-flash
API_HOST=0.0.0.0
API_PORT=8000
```

#### Step 3: Launch Services
```bash
docker compose up -d --build
docker compose ps
```

#### Step 4: Configure HTTPS (Let's Encrypt / Certbot)
Install Certbot on the host to provide SSL termination:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
```

---

### Option B: Render (PaaS) — *Recommended for Zero-DevOps Setup*

1. **Create Backend Web Service on Render:**
   - Connect your GitHub repository: `https://github.com/Akshit029/minor-project`.
   - **Environment:** Docker
   - **Dockerfile Path:** `./Dockerfile`
   - **Plan:** Starter (1 GB RAM minimum)
   - **Persistent Disk:** Attach a 5 GB disk mounted at `/app/outputs`.
   - **Environment Variables:**
     - `ALERT_THRESHOLD` = `0.60`
     - `GEMINI_API_KEY` = `your_gemini_api_key`
     - `PORT` = `8000`

2. **Create Frontend Web Service on Render:**
   - **Dockerfile Path:** `./frontend/Dockerfile`
   - **Plan:** Free or Starter
   - **Environment Variable:** `VITE_API_BASE_URL` = `https://your-backend.onrender.com`

---

### Option C: Railway

1. Install Railway CLI or connect GitHub repository in the Railway Dashboard.
2. Add a new service from the root `Dockerfile` (Backend).
3. Attach a Railway Volume mounted to `/app/outputs`.
4. Add a second service from `frontend/Dockerfile` (Frontend).
5. Set environment variable `VITE_API_BASE_URL` on the frontend pointing to the backend private or public URL.

---

## 3. Production Health Monitoring

The application includes an automated operational health check endpoint:
```bash
curl -f http://localhost:8000/api/health
```
Response format:
```json
{
  "status": "operational",
  "service": "Weather Reliability & Uncertainty AI Service (Weeks 1-9)",
  "gemini_api_key_configured": true,
  "configured_model": "gemini-2.0-flash",
  "alert_threshold": 0.60,
  "artifacts": {
    "week4_reliability_table": true,
    "week5_model_pipeline": true,
    "week7_shap_metadata": true,
    "week8_alerts_store": true,
    "week8_regional_geojson": true,
    "week8_lead_day_uncertainty": true
  },
  "supported_districts": ["Srinagar", "Jammu", "Anantnag", "Baramulla"]
}
```

---

## 4. Zero-Downtime Application Update Procedure

When updating code or deploying new models:
```bash
cd minor-project

# 1. Pull latest code
git pull origin main

# 2. Re-build and restart containers in rolling order
docker compose up -d --build --no-deps backend
docker compose up -d --build --no-deps frontend

# 3. Clean up dangling builder images
docker image prune -f

# 4. Verify health
docker compose ps
curl -f http://localhost:8000/api/health
```

---

## 5. External Cloud Dependencies & Action Required

For complete production operation, the following external items require user configuration:
1. **Google Gemini API Key:** Required for natural-language agent conversational reasoning (Week 6 assistant). If omitted, the system gracefully falls back to deterministic scientific rule execution.
2. **Domain Name & DNS Records:** A domain pointing an A record to your cloud server IP is required if SSL certificates are needed.
3. **SMTP Email Credentials (Optional):** Required only if external email delivery is desired (`ALERT_EMAIL_ENABLED=true`). In-app alerts function fully without SMTP.

