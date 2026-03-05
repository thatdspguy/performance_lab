import { useEffect, useState, useCallback } from 'react';
import { Container, Typography, Box, CircularProgress, Alert, Tab, Tabs, Button } from '@mui/material';
import AppSimulator from './components/AppSimulator';
import RegressionTable from './components/RegressionTable';
import { fetchApps, fetchRegressions, triggerPipeline } from './api/client';
import type { AppInfo, RegressionRecord, AppBenchmarkConfig } from './types';

export default function App() {
  const [apps, setApps] = useState<AppInfo[]>([]);
  const [regressions, setRegressions] = useState<RegressionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState(0);

  const [appConfigs, setAppConfigs] = useState<Record<string, AppBenchmarkConfig>>({});
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineResult, setPipelineResult] = useState<string | null>(null);
  const [pipelineError, setPipelineError] = useState<string | null>(null);

  useEffect(() => {
    fetchApps()
      .then(setApps)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const refreshRegressions = useCallback(() => {
    fetchRegressions().then(setRegressions).catch(console.error);
  }, []);

  useEffect(() => {
    refreshRegressions();
  }, [refreshRegressions]);

  const handleConfigChange = useCallback((slug: string, config: AppBenchmarkConfig) => {
    setAppConfigs((prev) => ({ ...prev, [slug]: config }));
  }, []);

  const handlePipeline = async () => {
    setPipelineLoading(true);
    setPipelineError(null);
    setPipelineResult(null);
    try {
      const result = await triggerPipeline(appConfigs);
      setPipelineResult(`Pushed as ${result.commit_id} — CI pipeline triggered.`);
      refreshRegressions();
    } catch (err) {
      setPipelineError(err instanceof Error ? err.message : 'Pipeline failed');
    } finally {
      setPipelineLoading(false);
    }
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Performance Lab
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Simulate commits and track performance regressions across applications.
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)}>
          <Tab label="Simulators" />
          <Tab label="Regressions" />
        </Tabs>
      </Box>

      {tab === 0 && (
        <Box>
          {apps.map((app) => (
            <AppSimulator
              key={app.slug}
              app={app}
              onSimulated={refreshRegressions}
              onConfigChange={handleConfigChange}
            />
          ))}
          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <Button
              variant="outlined"
              color="secondary"
              onClick={handlePipeline}
              disabled={pipelineLoading || Object.keys(appConfigs).length === 0}
            >
              {pipelineLoading ? <CircularProgress size={20} /> : 'Commit (Full Pipeline)'}
            </Button>
            {pipelineResult && <Alert severity="success" sx={{ flex: 1 }}>{pipelineResult}</Alert>}
            {pipelineError && <Alert severity="error" sx={{ flex: 1 }}>{pipelineError}</Alert>}
          </Box>
        </Box>
      )}

      {tab === 1 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Regression Events
          </Typography>
          <RegressionTable regressions={regressions} />
        </Box>
      )}
    </Container>
  );
}
