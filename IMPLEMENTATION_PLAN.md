# Performance Lab - Implementation Plan

## Automated Performance Regression Detection Platform

---

## Decisions Summary

| Decision             | Choice                                          |
|----------------------|--------------------------------------------------|
| Backend              | Python 3.12+ with FastAPI, managed by **uv**     |
| Frontend             | React + Vite + TypeScript                        |
| Metrics DB           | InfluxDB 2.x (Cloud for CI, local via Docker)    |
| Visualization        | Grafana (local via Docker Compose)               |
| Regression storage   | InfluxDB measurement (`regression_events`)       |
| CI/CD                | GitHub Actions (Phase 2 - deferred)              |
| Commit simulation    | Two modes: quick-simulate (local) and full pipeline (git+CI) |
| Build approach       | Incremental: core first, CI integration later    |

---

## Phase 1: Core Platform (Initial Build)

### What gets built

1. **Python backend** (FastAPI) - benchmark simulation, metrics writing, regression detection
2. **React frontend** (Vite + TS) - slider-based commit simulator UI
3. **InfluxDB 2.x** - local instance via Docker Compose for dev/demo
4. **Grafana** - local instance via Docker Compose, pre-configured dashboards
5. **Regression detection** - z-score analysis with results written to InfluxDB

### What is deferred to Phase 2

- GitHub Actions CI pipeline
- "Full pipeline" commit mode (git push + CI trigger)
- InfluxDB Cloud integration

---

## Architecture (Phase 1)

```
┌─────────────────────┐
│   React Frontend     │  (Vite dev server, port 5173)
│   - App sliders      │
│   - Commit button    │
│   - Regression table │
└────────┬────────────┘
         │ HTTP (REST)
         ▼
┌─────────────────────┐
│   FastAPI Backend    │  (uvicorn, port 8000)
│   - /api/simulate    │
│   - /api/metrics     │
│   - /api/regressions │
│   - /api/apps        │
└────────┬────────────┘
         │ InfluxDB client
         ▼
┌─────────────────────┐
│   InfluxDB 2.x      │  (Docker, port 8086)
│   - performance_metrics (measurement)
│   - regression_events   (measurement)
└────────┬────────────┘
         │ Flux queries
         ▼
┌─────────────────────┐
│   Grafana            │  (Docker, port 3000)
│   - Time series panels
│   - Regression annotations
│   - App filter variable
└─────────────────────┘
```

---

## Repository Structure

```
performance-lab/
├── pyproject.toml                  # uv project config (Python deps, metadata)
├── uv.lock                        # uv lockfile
├── docker-compose.yml              # InfluxDB + Grafana
├── .env.example                    # Environment variable template
│
├── backend/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entry point
│   ├── config.py                   # Settings (InfluxDB URL, org, bucket, token)
│   ├── models.py                   # Pydantic models (requests/responses)
│   ├── simulator.py                # Benchmark simulation engine
│   ├── metrics.py                  # InfluxDB read/write operations
│   ├── regression.py               # Z-score regression detection
│   └── apps.py                     # Application definitions & default configs
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts           # Typed API client for backend
│       ├── components/
│       │   ├── AppSimulator.tsx     # Per-app slider panel + commit button
│       │   ├── MetricSlider.tsx     # Reusable slider component
│       │   ├── RegressionTable.tsx  # Regression event log
│       │   └── MetricsChart.tsx     # Optional: inline charts (supplement Grafana)
│       └── types/
│           └── index.ts            # Shared TypeScript types
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── influxdb.yml        # Auto-provision InfluxDB datasource
│       └── dashboards/
│           ├── dashboard.yml       # Dashboard provisioning config
│           └── performance.json    # Pre-built Grafana dashboard
│
└── tests/
    ├── test_simulator.py
    ├── test_regression.py
    └── test_api.py
```

---

## Application Definitions

Each simulated application has default metric distributions.

| Application   | Slug         | CPU Mean | CPU Std | Mem Mean (MB) | Mem Std | Exec Mean (s) | Exec Std |
|---------------|--------------|----------|---------|---------------|---------|----------------|----------|
| Final Cut Pro | `final_cut`  | 45       | 4       | 800           | 50      | 2.5            | 0.3      |
| Logic Pro     | `logic_pro`  | 30       | 3       | 400           | 25      | 1.5            | 0.2      |
| Xcode         | `xcode`      | 55       | 5       | 1200          | 80      | 4.0            | 0.5      |

These defaults are the starting slider positions in the UI. Users adjust them to simulate drift/regressions.

---

## InfluxDB Schema

### Bucket: `performance_lab`

### Measurement: `performance_metrics`

| Type  | Name             | Description                     |
|-------|------------------|---------------------------------|
| Tag   | `application`    | App slug (e.g., `final_cut`)    |
| Tag   | `commit_id`      | Simulated commit hash           |
| Tag   | `commit_number`  | Sequential commit counter       |
| Field | `cpu_usage`      | Simulated CPU % (float)         |
| Field | `memory_usage`   | Simulated memory in MB (float)  |
| Field | `execution_time` | Simulated exec time in s (float)|

### Measurement: `regression_events`

| Type  | Name             | Description                     |
|-------|------------------|---------------------------------|
| Tag   | `application`    | App slug                        |
| Tag   | `commit_id`      | Commit that triggered detection |
| Tag   | `metric`         | Which metric regressed          |
| Tag   | `severity`       | `possible` (\|z\|>2) or `strong` (\|z\|>3) |
| Field | `value`          | The observed metric value        |
| Field | `z_score`        | Computed z-score                 |
| Field | `baseline_mean`  | Mean of baseline window          |
| Field | `baseline_std`   | Std dev of baseline window       |

---

## API Design

### `POST /api/simulate`

Trigger a simulated commit with benchmark run.

**Request body:**
```json
{
  "application": "final_cut",
  "cpu_mean": 45,
  "cpu_std": 4,
  "memory_mean": 800,
  "memory_std": 50,
  "execution_time_mean": 2.5,
  "execution_time_std": 0.3
}
```

**Response:**
```json
{
  "commit_id": "a1b2c3d4",
  "commit_number": 42,
  "application": "final_cut",
  "metrics": {
    "cpu_usage": 47.3,
    "memory_usage": 812.5,
    "execution_time": 2.61
  },
  "regressions": [
    {
      "metric": "cpu_usage",
      "value": 47.3,
      "z_score": 2.4,
      "baseline_mean": 38.1,
      "baseline_std": 3.8,
      "severity": "possible"
    }
  ]
}
```

### `GET /api/metrics?application={slug}&limit={n}`

Retrieve recent metrics for an application.

### `GET /api/regressions?application={slug}&limit={n}`

Retrieve recent regression events.

### `GET /api/apps`

List all application definitions with their default configs.

---

## Regression Detection Logic

```
For each metric in [cpu_usage, memory_usage, execution_time]:

    1. Query last 20 data points for this application from InfluxDB
    2. Compute baseline_mean and baseline_std
    3. If baseline_std == 0 or fewer than 5 data points: skip (insufficient data)
    4. Compute z = (new_value - baseline_mean) / baseline_std
    5. If |z| > 3: severity = "strong"
       Else if |z| > 2: severity = "possible"
       Else: no regression
    6. If regression detected: write to regression_events measurement
```

---

## Docker Compose Services

```yaml
services:
  influxdb:
    image: influxdb:2.7
    ports:
      - "8086:8086"
    volumes:
      - influxdb-data:/var/lib/influxdb2
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=adminpassword
      - DOCKER_INFLUXDB_INIT_ORG=performance-lab
      - DOCKER_INFLUXDB_INIT_BUCKET=performance_lab
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=dev-token-change-me

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - influxdb

volumes:
  influxdb-data:
  grafana-data:
```

---

## Python Dependencies (via uv)

```
fastapi
uvicorn[standard]
influxdb-client
pydantic
pydantic-settings
numpy
```

Dev dependencies:
```
pytest
httpx          # for testing FastAPI with TestClient
```

---

## Frontend Key Dependencies

```
react
react-dom
@types/react
@types/react-dom
typescript
vite
```

UI libraries (suggested):
```
@mui/material @emotion/react @emotion/styled   # Material UI for sliders, cards, layout
recharts                                         # Optional: inline charts in the UI
```

---

## Grafana Dashboard Specification

### Variables
- `application`: multi-value, query from `performance_metrics` tags

### Panels

1. **CPU Usage Over Time** - Time series, grouped by `application`
2. **Memory Usage Over Time** - Time series, grouped by `application`
3. **Execution Time Over Time** - Time series, grouped by `application`
4. **Regression Events Table** - Table panel querying `regression_events`
5. **Regression Annotations** - Overlay on time series panels, sourced from `regression_events`

---

## Development Workflow

### First-time setup

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Set up Python backend
uv sync

# 3. Run backend
uv run uvicorn backend.main:app --reload --port 8000

# 4. Set up and run frontend
cd frontend
npm install
npm run dev
```

### Ports

| Service   | Port |
|-----------|------|
| Frontend  | 5173 |
| Backend   | 8000 |
| InfluxDB  | 8086 |
| Grafana   | 3000 |

---

## Phase 2: CI Integration (Deferred)

When ready, Phase 2 adds:

1. **InfluxDB Cloud** account setup (free tier)
2. **GitHub Actions workflow** (`.github/workflows/benchmark.yml`)
   - Triggered on push to `main`
   - Reads metric config from a committed JSON file
   - Runs benchmark simulation
   - Writes metrics to InfluxDB Cloud
   - Runs regression detection
3. **"Full pipeline" mode** in the web UI
   - Pressing "Commit (Full Pipeline)" writes config JSON, commits, and pushes
   - CI picks it up and runs the benchmark
4. **Backend config** to switch between local and cloud InfluxDB via environment variables
5. **Grafana datasource** pointed at InfluxDB Cloud instead of / in addition to local

---

## Implementation Order (Phase 1)

| Step | Component                       | Description                                                |
|------|---------------------------------|------------------------------------------------------------|
| 1    | Project scaffolding             | uv init, pyproject.toml, folder structure, docker-compose  |
| 2    | Application definitions         | `apps.py` with default configs for 3 apps                 |
| 3    | Benchmark simulator             | `simulator.py` - generate metrics from normal distribution |
| 4    | InfluxDB integration            | `metrics.py` - write/read metrics using influxdb-client    |
| 5    | Regression detection            | `regression.py` - z-score analysis, write regression_events|
| 6    | FastAPI endpoints               | `main.py` - wire up /simulate, /metrics, /regressions, /apps |
| 7    | Backend tests                   | Unit tests for simulator, regression, API                  |
| 8    | React project setup             | Vite + TS scaffold, API client                             |
| 9    | Slider UI                       | AppSimulator component with sliders per app                |
| 10   | API integration                 | Connect frontend to backend, show results                  |
| 11   | Grafana provisioning            | Datasource + dashboard JSON auto-provisioned               |
| 12   | End-to-end validation           | Full flow: slider -> commit -> metrics -> Grafana          |
