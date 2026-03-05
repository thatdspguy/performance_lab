import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import MetricSlider from './MetricSlider';
import type { WorkflowInfo, WorkflowConfig } from '../types';

interface WorkflowControlsProps {
  workflow: WorkflowInfo;
  config: WorkflowConfig;
  onChange: (config: WorkflowConfig) => void;
}

export default function WorkflowControls({
  workflow,
  config,
  onChange,
}: WorkflowControlsProps) {
  return (
    <Accordion
      defaultExpanded
      sx={{
        '&:before': { display: 'none' },
        bgcolor: 'rgba(255,255,255,0.02)',
      }}
    >
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Typography fontWeight={600}>{workflow.name}</Typography>
      </AccordionSummary>
      <AccordionDetails>
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' },
            gap: 3,
          }}
        >
          <MetricSlider
            label="CPU Usage"
            value={config.cpu_mean}
            min={0}
            max={100}
            step={1}
            unit="%"
            onChange={(v) => onChange({ ...config, cpu_mean: v })}
          />
          <MetricSlider
            label="Memory Usage"
            value={config.memory_mean}
            min={0}
            max={4000}
            step={10}
            unit="MB"
            onChange={(v) => onChange({ ...config, memory_mean: v })}
          />
          <MetricSlider
            label="Execution Time"
            value={config.execution_time_mean}
            min={0}
            max={30}
            step={0.1}
            unit="s"
            onChange={(v) => onChange({ ...config, execution_time_mean: v })}
          />
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}
