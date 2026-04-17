import { useState } from 'react';
import {
  Box,
  Chip,
  Collapse,
  Stack,
  Typography,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import type { SourceRef } from '../types/index.js';

interface Props {
  sources: SourceRef[];
  compact?: boolean;
}

export function SourcesList({ sources, compact = false }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <Box>
      <Stack
        direction="row"
        spacing={0.5}
        onClick={() => setOpen(o => !o)}
        sx={{ alignItems: 'center', cursor: 'pointer', userSelect: 'none' }}
      >
        <Typography variant="caption" color="text.secondary" sx={{ textTransform: 'uppercase', letterSpacing: 1 }}>
          Sources ({sources.length})
        </Typography>
        {open ? <KeyboardArrowUpIcon sx={{ fontSize: 14, color: 'text.secondary' }} /> : <KeyboardArrowDownIcon sx={{ fontSize: 14, color: 'text.secondary' }} />}
      </Stack>
      <Collapse in={open}>
        <Stack spacing={0.5} mt={1}>
          {sources.map((s, i) => (
            <Stack key={i} direction="row" spacing={1} sx={{ alignItems: 'center' }} flexWrap="wrap">
              <Chip
                label={`p.${s.page_number}`}
                size="small"
                sx={{ fontSize: 10, height: 18 }}
              />
              {!compact && (
                <Typography variant="caption" color="text.secondary">{s.section}</Typography>
              )}
              <Typography variant="caption" sx={{ opacity: 0.5 }}>
                {(s.relevance_score * 100).toFixed(0)}%
              </Typography>
            </Stack>
          ))}
        </Stack>
      </Collapse>
    </Box>
  );
}
