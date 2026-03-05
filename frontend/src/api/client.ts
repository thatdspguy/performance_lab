import type {
  AppInfo,
  AppConfigResponse,
  SimulateRequest,
  SimulateResponse,
  RegressionRecord,
  WorkflowConfig,
  PipelineResponse,
} from '../types';

const BASE = '/api';

export async function fetchConfig(): Promise<AppConfigResponse> {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error(`Failed to fetch config: ${res.statusText}`);
  return res.json();
}

export async function fetchApps(): Promise<AppInfo[]> {
  const res = await fetch(`${BASE}/apps`);
  if (!res.ok) throw new Error(`Failed to fetch apps: ${res.statusText}`);
  return res.json();
}

export async function simulate(req: SimulateRequest): Promise<SimulateResponse> {
  const res = await fetch(`${BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}

export async function fetchRegressions(
  application?: string,
  workflow?: string,
  limit: number = 50,
): Promise<RegressionRecord[]> {
  const params = new URLSearchParams();
  if (application) params.set('application', application);
  if (workflow) params.set('workflow', workflow);
  params.set('limit', String(limit));
  const res = await fetch(`${BASE}/regressions?${params}`);
  if (!res.ok) throw new Error(`Failed to fetch regressions: ${res.statusText}`);
  return res.json();
}

export async function triggerPipeline(
  application: string,
  workflows: Record<string, WorkflowConfig>,
  commitMessage: string,
): Promise<PipelineResponse> {
  const res = await fetch(`${BASE}/pipeline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      application,
      workflows,
      commit_message: commitMessage,
    }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(`Pipeline failed: ${detail.detail || res.statusText}`);
  }
  return res.json();
}

export async function syncRepos(): Promise<{ success: boolean; repos: Record<string, string> }> {
  const res = await fetch(`${BASE}/repos/sync`, { method: 'POST' });
  if (!res.ok) throw new Error(`Repo sync failed: ${res.statusText}`);
  return res.json();
}
