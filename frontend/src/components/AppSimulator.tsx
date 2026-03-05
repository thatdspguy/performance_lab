import { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Button, Alert, Box, CircularProgress } from '@mui/material';
import MetricSlider from './MetricSlider';
import { simulate } from '../api/client';
import type { AppInfo, SimulateResponse, RegressionInfo, AppBenchmarkConfig } from '../types';

interface AppSimulatorProps {
  app: AppInfo;
  onSimulated: () => void;
  onConfigChange: (slug: string, config: AppBenchmarkConfig) => void;
}

export default function AppSimulator({ app, onSimulated, onConfigChange }: AppSimulatorProps) {
  const [cpuMean, setCpuMean] = useState(app.cpu_mean);
  const [cpuStd, setCpuStd] = useState(app.cpu_std);
  const [memMean, setMemMean] = useState(app.memory_mean);
  const [memStd, setMemStd] = useState(app.memory_std);
  const [execMean, setExecMean] = useState(app.execution_time_mean);
  const [execStd, setExecStd] = useState(app.execution_time_std);

  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState<SimulateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    onConfigChange(app.slug, {
      cpu_mean: cpuMean,
      cpu_std: cpuStd,
      memory_mean: memMean,
      memory_std: memStd,
      execution_time_mean: execMean,
      execution_time_std: execStd,
    });
  }, [cpuMean, cpuStd, memMean, memStd, execMean, execStd, app.slug, onConfigChange]);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await simulate({
        application: app.slug,
        cpu_mean: cpuMean,
        cpu_std: cpuStd,
        memory_mean: memMean,
        memory_std: memStd,
        execution_time_mean: execMean,
        execution_time_std: execStd,
      });
      setLastResult(result);
      onSimulated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          {app.name}
        </Typography>

        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <MetricSlider
            label="CPU Mean"
            value={cpuMean}
            min={0}
            max={100}
            step={1}
            unit="%"
            onChange={setCpuMean}
          />
          <MetricSlider
            label="CPU Std Dev"
            value={cpuStd}
            min={0}
            max={20}
            step={0.5}
            unit="%"
            onChange={setCpuStd}
          />
          <MetricSlider
            label="Memory Mean"
            value={memMean}
            min={0}
            max={4000}
            step={10}
            unit="MB"
            onChange={setMemMean}
          />
          <MetricSlider
            label="Memory Std Dev"
            value={memStd}
            min={0}
            max={200}
            step={5}
            unit="MB"
            onChange={setMemStd}
          />
          <MetricSlider
            label="Exec Time Mean"
            value={execMean}
            min={0}
            max={20}
            step={0.1}
            unit="s"
            onChange={setExecMean}
          />
          <MetricSlider
            label="Exec Time Std Dev"
            value={execStd}
            min={0}
            max={5}
            step={0.05}
            unit="s"
            onChange={setExecStd}
          />
        </Box>

        <Button
          variant="contained"
          onClick={handleSimulate}
          disabled={loading}
          sx={{ mt: 2 }}
        >
          {loading ? <CircularProgress size={20} /> : 'Simulate Commit'}
        </Button>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {lastResult && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2">
              Commit <code>{lastResult.commit_id}</code> (#{lastResult.commit_number})
            </Typography>
            <Typography variant="body2">
              CPU: {lastResult.metrics.cpu_usage}% | Memory: {lastResult.metrics.memory_usage} MB |
              Exec: {lastResult.metrics.execution_time}s
            </Typography>
            {lastResult.regressions.length > 0 && (
              <Alert severity="warning" sx={{ mt: 1 }}>
                {lastResult.regressions.length} regression(s) detected:{' '}
                {lastResult.regressions.map((r: RegressionInfo) => `${r.metric} (${r.severity})`).join(', ')}
              </Alert>
            )}
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
