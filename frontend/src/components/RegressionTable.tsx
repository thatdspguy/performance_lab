import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Typography,
} from '@mui/material';
import type { RegressionRecord } from '../types';

interface RegressionTableProps {
  regressions: RegressionRecord[];
}

export default function RegressionTable({ regressions }: RegressionTableProps) {
  if (regressions.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        No regressions detected yet.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>Application</TableCell>
            <TableCell>Metric</TableCell>
            <TableCell>Value</TableCell>
            <TableCell>Z-Score</TableCell>
            <TableCell>Baseline Mean</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Commit</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {regressions.map((r, i) => (
            <TableRow key={`${r.commit_id}-${r.metric}-${i}`}>
              <TableCell>{new Date(r.time).toLocaleString()}</TableCell>
              <TableCell>{r.application}</TableCell>
              <TableCell>{r.metric}</TableCell>
              <TableCell>{r.value.toFixed(2)}</TableCell>
              <TableCell>{r.z_score.toFixed(2)}</TableCell>
              <TableCell>{r.baseline_mean.toFixed(2)}</TableCell>
              <TableCell>
                <Chip
                  label={r.severity}
                  size="small"
                  color={r.severity === 'strong' ? 'error' : 'warning'}
                />
              </TableCell>
              <TableCell>
                <code>{r.commit_id}</code>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
