import { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Tab,
  Tabs,
} from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import AppDashboard from './components/AppDashboard';
import { fetchApps, fetchConfig } from './api/client';
import type { AppInfo } from './types';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#6C9BFF' },
    secondary: { main: '#FF6B9D' },
    background: {
      default: '#0A0E1A',
      paper: '#111827',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(255,255,255,0.06)',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          fontSize: '0.95rem',
        },
      },
    },
  },
});

export default function App() {
  const [apps, setApps] = useState<AppInfo[]>([]);
  const [grafanaUrls, setGrafanaUrls] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState(0);

  useEffect(() => {
    Promise.all([
      fetchApps().then(setApps),
      fetchConfig().then((cfg) => setGrafanaUrls(cfg.grafana_urls)),
    ])
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Container sx={{ mt: 8, textAlign: 'center' }}>
          <CircularProgress />
        </Container>
      </ThemeProvider>
    );
  }

  if (error) {
    return (
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Container sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ mt: 3, mb: 4 }}>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Performance Lab
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Monitor and control performance benchmarks across applications.
          </Typography>
        </Box>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            variant="fullWidth"
            sx={{
              '& .MuiTabs-indicator': {
                height: 3,
                borderRadius: 2,
              },
            }}
          >
            {apps.map((app) => (
              <Tab key={app.slug} label={app.name} />
            ))}
          </Tabs>
        </Box>

        {apps.map((app, index) =>
          tab === index ? (
            <AppDashboard
              key={app.slug}
              app={app}
              grafanaUrl={grafanaUrls[app.slug] || ''}
            />
          ) : null,
        )}
      </Container>
    </ThemeProvider>
  );
}
