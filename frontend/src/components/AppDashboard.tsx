import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  TextField,
  Card,
  CardContent,
  Divider,
} from '@mui/material';
import WorkflowControls from './WorkflowControls';
import GrafanaDashboard from './GrafanaDashboard';
import RegressionTable from './RegressionTable';
import { triggerPipeline, fetchRegressions } from '../api/client';
import type { AppInfo, WorkflowConfig, RegressionRecord } from '../types';

interface AppDashboardProps {
  app: AppInfo;
  grafanaUrl: string;
}

export default function AppDashboard({ app, grafanaUrl }: AppDashboardProps) {
  const [workflowConfigs, setWorkflowConfigs] = useState<Record<string, WorkflowConfig>>(() => {
    const initial: Record<string, WorkflowConfig> = {};
    for (const wf of app.workflows) {
      initial[wf.slug] = {
        cpu_mean: wf.cpu_mean,
        memory_mean: wf.memory_mean,
        execution_time_mean: wf.execution_time_mean,
      };
    }
    return initial;
  });

  const [commitMessage, setCommitMessage] = useState('');
  const [commitMessageError, setCommitMessageError] = useState(false);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<string | null>(null);
  const [pipelineError, setPipelineError] = useState<string | null>(null);
  const [regressions, setRegressions] = useState<RegressionRecord[]>([]);

  const refreshRegressions = useCallback(() => {
    fetchRegressions(app.slug).then(setRegressions).catch(console.error);
  }, [app.slug]);

  useEffect(() => {
    refreshRegressions();
  }, [refreshRegressions]);

  const handleWorkflowChange = (workflowSlug: string, config: WorkflowConfig) => {
    setWorkflowConfigs((prev) => ({ ...prev, [workflowSlug]: config }));
  };

  const handlePipeline = async () => {
    if (!commitMessage.trim()) {
      setCommitMessageError(true);
      return;
    }
    setPipelineLoading(true);
    setPipelineError(null);
    setPipelineResult(null);
    try {
      const result = await triggerPipeline(app.slug, workflowConfigs, commitMessage);
      setPipelineResult(`Pushed as ${result.commit_id} — CI pipeline triggered.`);
      refreshRegressions();
      setTimeout(() => setPipelineResult(null), 10000);
    } catch (err) {
      setPipelineError(err instanceof Error ? err.message : 'Pipeline failed');
      setTimeout(() => setPipelineError(null), 10000);
    } finally {
      setPipelineLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Workflow Controls */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Workflow Benchmarks
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Configure performance metrics for each workflow, then commit and push to trigger CI.
          </Typography>

          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {app.workflows.map((wf) => (
              <WorkflowControls
                key={wf.slug}
                workflow={wf}
                config={workflowConfigs[wf.slug]}
                onChange={(config) => handleWorkflowChange(wf.slug, config)}
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {/* Commit Section */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Commit to {app.name}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-start', mb: 2 }}>
            <TextField
              size="small"
              label="Commit message"
              value={commitMessage}
              onChange={(e) => {
                setCommitMessage(e.target.value);
                if (commitMessageError) setCommitMessageError(false);
              }}
              error={commitMessageError}
              helperText={commitMessageError ? 'A commit message is required' : undefined}
              placeholder="Describe your changes..."
              sx={{ flex: 1 }}
            />
            <Button
              variant="contained"
              onClick={handlePipeline}
              disabled={pipelineLoading}
              sx={{ minWidth: 160, height: 40 }}
            >
              {pipelineLoading ? <CircularProgress size={20} /> : 'Commit & Push'}
            </Button>
          </Box>
          {pipelineResult && <Alert severity="success" sx={{ mb: 1 }}>{pipelineResult}</Alert>}
          {pipelineError && <Alert severity="error" sx={{ mb: 1 }}>{pipelineError}</Alert>}
        </CardContent>
      </Card>

      {/* Grafana Dashboard */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Performance Dashboard
          </Typography>
          <GrafanaDashboard url={grafanaUrl} title={`${app.name} Performance`} />
        </CardContent>
      </Card>

      {/* Regressions */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Detected Regressions
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <RegressionTable regressions={regressions} />
        </CardContent>
      </Card>
    </Box>
  );
}
