import { Box, Typography, Alert } from '@mui/material';

interface GrafanaDashboardProps {
  url: string;
  title: string;
}

export default function GrafanaDashboard({ url, title }: GrafanaDashboardProps) {
  if (!url) {
    return (
      <Alert severity="info" variant="outlined">
        <Typography variant="body2">
          Grafana dashboard URL not configured. Run{' '}
          <code>docker compose up -d</code> to start Grafana OSS, then set the
          GRAFANA_*_URL variables in your .env file (see .env.example).
        </Typography>
      </Alert>
    );
  }

  return (
    <Box
      sx={{
        width: '100%',
        borderRadius: 1,
        overflow: 'hidden',
        border: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <iframe
        src={url}
        title={title}
        width="100%"
        height="1400"
        style={{ border: 'none', display: 'block' }}
      />
    </Box>
  );
}
