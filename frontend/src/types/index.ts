export interface AppInfo {
  name: string;
  slug: string;
  cpu_mean: number;
  cpu_std: number;
  memory_mean: number;
  memory_std: number;
  execution_time_mean: number;
  execution_time_std: number;
}

export interface SimulateRequest {
  application: string;
  cpu_mean: number;
  cpu_std: number;
  memory_mean: number;
  memory_std: number;
  execution_time_mean: number;
  execution_time_std: number;
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
  metrics: MetricsResult;
  regressions: RegressionInfo[];
}

export interface RegressionRecord {
  time: string;
  application: string;
  commit_id: string;
  metric: string;
  severity: string;
  value: number;
  z_score: number;
  baseline_mean: number;
  baseline_std: number;
}

export interface AppBenchmarkConfig {
  cpu_mean: number;
  cpu_std: number;
  memory_mean: number;
  memory_std: number;
  execution_time_mean: number;
  execution_time_std: number;
}

export interface PipelineResponse {
  success: boolean;
  commit_id: string | null;
  message: string;
}
