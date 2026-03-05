# Grafana OSS Setup

The Performance Lab uses a self-hosted Grafana OSS instance (via Docker) to visualize performance metrics. This enables iframe embedding, which is not available on Grafana Cloud.

## Docker Compose

The `docker-compose.yml` at the project root runs Grafana OSS 11.6:

```bash
docker compose up -d
```

Grafana is available at http://localhost:3000.

## Embedding Configuration

The Docker Compose file pre-configures these Grafana settings:

| Setting | Value | Purpose |
|---|---|---|
| `GF_SECURITY_ALLOW_EMBEDDING` | `true` | Allow loading Grafana in iframes |
| `GF_SECURITY_COOKIE_SAMESITE` | `none` | Allow cross-origin cookies for iframe |
| `GF_AUTH_ANONYMOUS_ENABLED` | `true` | Let iframes load without login |
| `GF_AUTH_ANONYMOUS_ORG_ROLE` | `Viewer` | Read-only access for anonymous users |

## Data Source Provisioning

The InfluxDB data source is auto-provisioned from `grafana/provisioning/datasources/influxdb.yml`. It reads InfluxDB credentials from environment variables passed through Docker Compose (which reads them from your `.env` file):

- `INFLUXDB_URL` — InfluxDB Cloud URL
- `INFLUXDB_TOKEN` — API token
- `INFLUXDB_ORG` — Organization ID
- `INFLUXDB_BUCKET` — Bucket name

The data source uses Grafana's `$__env{VAR}` syntax for environment variable expansion.

## Dashboard Provisioning

Three per-app dashboards are auto-loaded from `grafana/dashboards/`:

| Dashboard | UID | File |
|---|---|---|
| Final Cut Pro Performance | `final-cut-performance` | `grafana/dashboards/final-cut-dashboard.json` |
| Logic Pro Performance | `logic-pro-performance` | `grafana/dashboards/logic-pro-dashboard.json` |
| Xcode Performance | `xcode-performance` | `grafana/dashboards/xcode-dashboard.json` |

The provisioning config (`grafana/provisioning/dashboards/dashboards.yml`) scans for changes every 30 seconds.

## Dashboard Embed URLs

The frontend embeds Grafana dashboards using URLs configured in `.env`:

```
GRAFANA_FINAL_CUT_URL=http://localhost:3000/d/final-cut-performance/final-cut-pro-performance?orgId=1&kiosk
GRAFANA_LOGIC_PRO_URL=http://localhost:3000/d/logic-pro-performance/logic-pro-performance?orgId=1&kiosk
GRAFANA_XCODE_URL=http://localhost:3000/d/xcode-performance/xcode-performance?orgId=1&kiosk
```

The `?kiosk` parameter hides the Grafana header and sidebar for a clean embedded view.

## Customizing Time Range

Each dashboard has a default time range defined in its JSON file. To change it, edit the `"time"` object near the bottom of each dashboard file in `grafana/dashboards/`:

```json
"time": {
  "from": "now-3h",
  "to": "now"
}
```

Common values: `now-1h`, `now-3h`, `now-6h`, `now-12h`, `now-1d`, `now-7d`, `now-30d`.

After editing, Grafana will pick up changes within 30 seconds (or restart the container).

## Customizing Dashboards

The provisioned dashboards are read-only in the Grafana UI since they're file-provisioned. To make edits:

1. Edit the JSON files in `grafana/dashboards/` directly
2. Or copy a dashboard in the Grafana UI (Save As), which creates an editable copy

Each dashboard contains:
- **Workflow template variable** — filter by workflow
- **Per-workflow rows** — each with CPU, Memory, and Execution Time time series panels
- **Regression events table** — sortable by time, with severity color coding
- **Regression annotations** — red (strong) and orange (possible) markers on time series
