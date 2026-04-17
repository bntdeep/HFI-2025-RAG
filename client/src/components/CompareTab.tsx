import {
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  FormControlLabel,
  FormGroup,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useCompareStore } from '../store/compareStore.js';
import { DEFAULT_COMPARE_PARAMS } from '../constants.js';
import { ButterflyChart } from './charts/ButterflyChart.js';
import { SourcesList } from './SourcesList.js';
import { CountryAutocomplete } from './CountryAutocomplete.js';

export function CompareTab() {
  const { countryA, countryB, selectedParams, result, isLoading, error, setCountryA, setCountryB, toggleParam, runCompare } =
    useCompareStore();

  const canCompare = !!countryA && !!countryB && countryA !== countryB && selectedParams.length > 0;

  return (
    <Stack spacing={3}>
      {/* Country selectors */}
      <Paper sx={{ p: 2 }}>
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ alignItems: 'center' }}>
          <CountryAutocomplete
            label="Country A"
            value={countryA}
            onChange={setCountryA}
            exclude={countryB}
            minWidth={220}
          />

          <CompareArrowsIcon sx={{ color: 'text.secondary', flexShrink: 0 }} />

          <CountryAutocomplete
            label="Country B"
            value={countryB}
            onChange={setCountryB}
            exclude={countryA}
            minWidth={220}
          />

          <Box flex={1} />

          <Button
            variant="contained"
            disabled={!canCompare || isLoading}
            onClick={runCompare}
            startIcon={isLoading ? <CircularProgress size={14} color="inherit" /> : undefined}
          >
            {isLoading ? 'Comparing…' : 'Compare'}
          </Button>
        </Stack>

        {/* Parameter checkboxes */}
        <FormGroup row sx={{ mt: 1.5, gap: 0.5 }}>
          {DEFAULT_COMPARE_PARAMS.map(p => (
            <FormControlLabel
              key={p}
              control={
                <Checkbox
                  size="small"
                  checked={selectedParams.includes(p)}
                  onChange={() => toggleParam(p)}
                />
              }
              label={<Typography variant="body2">{p}</Typography>}
              sx={{ mr: 1 }}
            />
          ))}
        </FormGroup>
      </Paper>

      {error && (
        <Paper sx={{ p: 2, borderColor: 'error.main', border: 1 }}>
          <Typography color="error" variant="body2">{error}</Typography>
        </Paper>
      )}

      {result && (
        <>
          {/* Butterfly chart */}
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mb: 1.5 }}>
              <Chip label={result.countries[0]} size="small" sx={{ bgcolor: '#4a9eff22', color: '#4a9eff' }} />
              <Typography variant="body2" color="text.secondary">vs</Typography>
              <Chip label={result.countries[1]} size="small" sx={{ bgcolor: '#ff6b6b22', color: '#ff6b6b' }} />
            </Stack>
            <ButterflyChart
              data={result.butterfly_data}
              countries={result.countries as [string, string]}
            />
          </Paper>

          {/* Analysis text */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block', textTransform: 'uppercase', letterSpacing: 1 }}>
              Analysis
            </Typography>
            <Box sx={{ '& p': { mt: 0.5, mb: 0.5 }, '& table': { borderCollapse: 'collapse', width: '100%' }, '& td,& th': { border: '1px solid rgba(255,255,255,0.1)', px: 1, py: 0.5, fontSize: 12 } }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{result.response_text}</ReactMarkdown>
            </Box>
          </Paper>

          {result.sources.length > 0 && <SourcesList sources={result.sources} />}
        </>
      )}
    </Stack>
  );
}
