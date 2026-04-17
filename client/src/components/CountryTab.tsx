import {
  Box,
  Button,
  Chip,
  CircularProgress,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from '@mui/material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useCountryStore } from '../store/countryStore.js';
import { RadarChart } from './charts/RadarChart.js';
import { SourcesList } from './SourcesList.js';
import { RADAR_SUBCATEGORIES } from '../constants.js';
import { CountryAutocomplete } from './CountryAutocomplete.js';

function SubcategoryRow({ label, value }: { label: string; value: number | null }) {
  const v = value ?? 0;
  return (
    <Stack direction="row" spacing={1.5} sx={{ alignItems: 'center', py: 0.5 }}>
      <Typography variant="body2" sx={{ minWidth: 180, color: 'text.secondary' }}>{label}</Typography>
      <LinearProgress
        variant="determinate"
        value={v * 10}
        sx={{ flex: 1, height: 6, borderRadius: 3, bgcolor: 'rgba(255,255,255,0.06)' }}
      />
      <Typography variant="body2" sx={{ minWidth: 36, textAlign: 'right', fontVariantNumeric: 'tabular-nums' }}>
        {value !== null ? v.toFixed(1) : '—'}
      </Typography>
    </Stack>
  );
}

// Maps radar display names to all possible dict keys the API may return
const RADAR_KEY_MAP: Record<string, string[]> = {
  'Rule of Law': ['Rule of Law', 'rule_of_law', 'pf_rol', 'rol'],
  'Security & Safety': ['Security & Safety', 'Security', 'security', 'security_and_safety', 'pf_ss', 'ss', 'Security and Safety'],
  'Movement': ['Movement', 'movement', 'pf_movement'],
  'Religion': ['Religion', 'religion', 'pf_religion'],
  'Association & Assembly': ['Association & Assembly', 'Association', 'association', 'association_assembly_civil_society', 'pf_association', 'Association Assembly Civil Society'],
  'Expression & Information': ['Expression & Information', 'Expression', 'expression', 'expression_and_information', 'pf_expression', 'Expression and Information'],
  'Relationships': ['Relationships', 'relationships', 'pf_identity'],
};

function lookupSubcategory(subcategories: Record<string, number>, displayName: string): number {
  const keys = RADAR_KEY_MAP[displayName] ?? [displayName];
  for (const k of keys) {
    if (subcategories[k] !== undefined) return subcategories[k];
  }
  return 0;
}

// Keys that are already shown in the hardcoded SubcategoryRow list above
const KNOWN_SUBCATEGORY_KEYS = new Set([
  'rule_of_law', 'Rule of Law', 'pf_rol', 'rol',
  'security_and_safety', 'Security & Safety', 'Security', 'security', 'pf_ss', 'ss', 'Security and Safety',
  'movement', 'Movement', 'pf_movement',
  'religion', 'Religion', 'pf_religion',
  'expression_and_information', 'Expression & Information', 'Expression', 'expression', 'pf_expression', 'Expression and Information',
  'association_assembly_civil_society', 'Association & Assembly', 'Association', 'association', 'pf_association', 'Association Assembly Civil Society',
  'relationships', 'Relationships', 'pf_identity',
]);

function toLabel(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

export function CountryTab() {
  const { selectedCountry, result, isLoading, error, setCountry, runProfile } = useCountryStore();

  const radarData = result
    ? RADAR_SUBCATEGORIES.map(s => ({
        subject: s,
        value: lookupSubcategory(result.subcategories, s),
      }))
    : [];

  return (
    <Stack spacing={3}>
      {/* Selector */}
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" spacing={2} sx={{ alignItems: 'center' }}>
          <CountryAutocomplete
            label="Country"
            value={selectedCountry}
            onChange={setCountry}
            minWidth={240}
          />
          <Button
            variant="contained"
            disabled={!selectedCountry || isLoading}
            onClick={runProfile}
            startIcon={isLoading ? <CircularProgress size={14} color="inherit" /> : undefined}
          >
            {isLoading ? 'Loading…' : 'Profile'}
          </Button>
        </Stack>
      </Paper>

      {error && (
        <Paper sx={{ p: 2, border: 1, borderColor: 'error.main' }}>
          <Typography color="error" variant="body2">{error}</Typography>
        </Paper>
      )}

      {result && (
        <>
          {/* Header card */}
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" sx={{ alignItems: 'center' }} spacing={2} mb={2}>
              <Typography variant="h4">{result.flag}</Typography>
              <Box>
                <Typography variant="h6">{result.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Rank #{result.overall_rank} · Score {result.overall_score?.toFixed(2)}
                </Typography>
              </Box>
            </Stack>
            <Stack direction="row" spacing={2} flexWrap="wrap">
              <Chip label={`Personal Freedom ${result.personal_freedom_score?.toFixed(2)}`} size="small" sx={{ bgcolor: '#4a9eff22', color: '#4a9eff' }} />
              <Chip label={`Economic Freedom ${result.economic_freedom_score?.toFixed(2)}`} size="small" sx={{ bgcolor: '#a8ff6b22', color: '#a8ff6b' }} />
              {result.movement !== null && (
                <Chip label={`Movement ${result.movement?.toFixed(2)}`} size="small" sx={{ bgcolor: '#ff9a3c22', color: '#ff9a3c' }} />
              )}
              {result.religion !== null && (
                <Chip label={`Religion ${result.religion?.toFixed(2)}`} size="small" sx={{ bgcolor: '#c46bff22', color: '#c46bff' }} />
              )}
            </Stack>
          </Paper>

          {/* Radar + subcategories */}
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
            <Paper sx={{ p: 2, flex: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>
                Personal Freedom Radar
              </Typography>
              <RadarChart data={radarData} />
            </Paper>

            <Paper sx={{ p: 2, flex: 1 }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>
                Personal Freedom Breakdown
              </Typography>
              <SubcategoryRow label="Rule of Law" value={result.rule_of_law ?? result.subcategories['rule_of_law'] ?? null} />
              <SubcategoryRow label="Security & Safety" value={result.security ?? result.subcategories['security_and_safety'] ?? null} />
              <SubcategoryRow label="Movement" value={result.movement ?? result.subcategories['movement'] ?? null} />
              <SubcategoryRow label="Religion" value={result.religion ?? result.subcategories['religion'] ?? null} />
              <SubcategoryRow label="Expression & Information" value={result.expression ?? result.subcategories['expression_and_information'] ?? null} />
              <SubcategoryRow label="Association & Assembly" value={result.association ?? result.subcategories['association_assembly_civil_society'] ?? null} />
              <SubcategoryRow label="Relationships" value={result.subcategories['relationships'] ?? null} />
              {/* Remaining subcategories from dict */}
              {Object.entries(result.subcategories)
                .filter(([k]) => !KNOWN_SUBCATEGORY_KEYS.has(k))
                .map(([k, v]) => (
                  <SubcategoryRow key={k} label={toLabel(k)} value={v} />
                ))}
            </Paper>
          </Stack>

          {/* Strengths / Weaknesses */}
          {(result.strengths.length > 0 || result.weaknesses.length > 0) && (
            <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
              {result.strengths.length > 0 && (
                <Paper sx={{ p: 2, flex: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>
                    Strengths
                  </Typography>
                  {result.strengths.map((s, i) => (
                    <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>· {s}</Typography>
                  ))}
                </Paper>
              )}
              {result.weaknesses.length > 0 && (
                <Paper sx={{ p: 2, flex: 1 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1, textTransform: 'uppercase', letterSpacing: 1 }}>
                    Weaknesses
                  </Typography>
                  {result.weaknesses.map((w, i) => (
                    <Typography key={i} variant="body2" sx={{ mb: 0.5 }}>· {w}</Typography>
                  ))}
                </Paper>
              )}
            </Stack>
          )}

          {/* Analysis text */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block', textTransform: 'uppercase', letterSpacing: 1 }}>
              Profile Analysis
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
