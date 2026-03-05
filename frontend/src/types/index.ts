export interface WorkflowInfo {
  name: string;
  slug: string;
  cpu_mean: number;
  memory_mean: number;
  execution_time_mean: number;
}

export interface AppInfo {
  name: string;
  slug: string;
  repo_url: string;
  workflows: WorkflowInfo[];
}

export interface WorkflowConfig {
  cpu_mean: number;
  memory_mean: number;
  execution_time_mean: number;
}

export interface SimulateRequest {
  application: string;
  workflow: string;
  cpu_mean: number;
  memory_mean: number;
  execution_time_mean: number;
}

export interface MetricsResult {
  cpu_usage: number;
  memory_usage: number;
  execution_time: number;
}

export interface RegressionInfo {
  metric: string;
  value: number;
  z_score: number;
  baseline_mean: number;
  baseline_std: number;
  severity: string;
}

export interface SimulateResponse {
  commit_id: string;
  commit_number: number;
  application: string;
  workflow: string;
  metrics: MetricsResult;
  regressions: RegressionInfo[];
}

export interface RegressionRecord {
  time: string;
  application: string;
  workflow: string;
  commit_id: string;
  metric: string;
  severity: string;
  value: number;
  z_score: number;
  baseline_mean: number;
  baseline_std: number;
}

export interface PipelineRequest {
  application: string;
  workflows: Record<string, WorkflowConfig>;
  commit_message?: string;
}

export interface PipelineResponse {
  success: boolean;
  commit_id: string | null;
  message: string;
}

export interface AppConfigResponse {
  grafana_urls: Record<string, string>;
}
