import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import { useMetaStore } from '../store/metaStore.js';

interface Props {
  label: string;
  value: string;
  onChange(v: string): void;
  exclude?: string;
  size?: 'small' | 'medium';
  minWidth?: number;
}

export function CountryAutocomplete({ label, value, onChange, exclude, size = 'small', minWidth = 200 }: Props) {
  const countries = useMetaStore(s => s.countries);
  const sorted = [...countries]
    .filter(c => c !== exclude)
    .sort((a, b) => a.localeCompare(b));

  return (
    <Autocomplete
      value={value || null}
      onChange={(_, v) => onChange(v ?? '')}
      options={sorted}
      size={size}
      sx={{ minWidth }}
      renderInput={(params) => (
        <TextField {...params} label={label} placeholder="Type to search…" />
      )}
      autoHighlight
      openOnFocus
      clearOnEscape
      noOptionsText="No countries found"
    />
  );
}
