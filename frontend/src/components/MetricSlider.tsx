import { Slider, Typography, Box } from '@mui/material';

interface MetricSliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  unit: string;
  onChange: (value: number) => void;
}

export default function MetricSlider({
  label,
  value,
  min,
  max,
  step,
  unit,
  onChange,
}: MetricSliderProps) {
  return (
    <Box sx={{ mb: 2 }}>
      <Typography variant="body2" gutterBottom>
        {label}: {value} {unit}
      </Typography>
      <Slider
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(_, v) => onChange(v as number)}
        valueLabelDisplay="auto"
        size="small"
      />
    </Box>
  );
}
