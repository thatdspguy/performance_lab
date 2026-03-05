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
      <Typography variant="body2" color="text.secondary">
        No regressions detected yet.
      </Typography>
    );
  }

  return (
    <TableContainer component={Paper} variant="outlined">
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>Workflow</TableCell>
            <TableCell>Metric</TableCell>
            <TableCell align="right">Value</TableCell>
            <TableCell align="right">Z-Score</TableCell>
            <TableCell align="right">Baseline Mean</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>Commit</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {regressions.map((r, i) => (
            <TableRow key={`${r.commit_id}-${r.metric}-${i}`}>
              <TableCell>{new Date(r.time).toLocaleString()}</TableCell>
              <TableCell>{r.workflow}</TableCell>
              <TableCell>{r.metric}</TableCell>
              <TableCell align="right">{r.value.toFixed(2)}</TableCell>
              <TableCell align="right">{r.z_score.toFixed(2)}</TableCell>
              <TableCell align="right">{r.baseline_mean.toFixed(2)}</TableCell>
              <TableCell>
                <Chip
                  label={r.severity}
                  color={r.severity === 'strong' ? 'error' : 'warning'}
                  size="small"
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
