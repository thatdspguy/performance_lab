# Performance Lab Frontend

React dashboard for the Performance Lab platform.

## Tech Stack

- **React 19** with TypeScript
- **Vite 7** for dev server and bundling
- **Material UI 7** (`@mui/material`) for components and dark theme
- **`@mui/icons-material`** for icons

## Development

```bash
npm install
npm run dev
```

The dev server runs on http://localhost:5173 and proxies `/api/*` requests to the backend at `http://localhost:8001` (configured in `vite.config.ts`).

## Components

| Component | Description |
|---|---|
| `App.tsx` | Root component with per-app tabs (Final Cut Pro, Logic Pro, Xcode) |
| `AppDashboard.tsx` | All-in-one per-app view: workflow controls, commit section, Grafana iframe, regressions |
| `WorkflowControls.tsx` | Expandable accordion with 3 metric sliders per workflow |
| `GrafanaDashboard.tsx` | Embedded Grafana dashboard via iframe |
| `MetricSlider.tsx` | Reusable labeled slider for a single metric |
| `RegressionTable.tsx` | Table of detected regression events with severity chips |

## API Client

`src/api/client.ts` provides typed functions for all backend endpoints:

- `fetchApps()` / `fetchConfig()` — load app definitions and Grafana URLs
- `triggerPipeline()` — commit & push workflow configs to a mock repo
- `fetchRegressions()` — query regression events
- `simulate()` — simulate a single workflow run (used by CLI)
- `syncRepos()` — clone/pull mock repos
