import { useRef, useEffect } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import { useDebugStore } from '../store/debugStore.js';

const EVENT_COLOR: Record<string, string> = {
  node_start: '#4a9eff',
  node_end: '#a8ff6b',
  retrieval: '#ff9a3c',
  llm_call: '#c46bff',
  error: '#ff6b6b',
};

export function DebugConsole() {
  const { events, isOpen, toggle, clear } = useDebugStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events, isOpen]);

  return (
    <Drawer
      anchor="bottom"
      open={isOpen}
      onClose={toggle}
      PaperProps={{
        sx: {
          height: '40vh',
          bgcolor: '#0a0a0a',
          borderTop: '1px solid rgba(255,255,255,0.1)',
        },
      }}
    >
      <Stack direction="row" sx={{ alignItems: 'center' }} px={2} py={1} borderBottom="1px solid rgba(255,255,255,0.08)">
        <Typography variant="caption" sx={{ textTransform: 'uppercase', letterSpacing: 1, color: 'text.secondary', flex: 1 }}>
          Debug Console ({events.length})
        </Typography>
        <Tooltip title="Clear">
          <IconButton size="small" onClick={clear}>
            <DeleteOutlinedIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        <IconButton size="small" onClick={toggle}>
          <CloseIcon fontSize="small" />
        </IconButton>
      </Stack>
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          px: 2,
          py: 1,
          fontFamily: 'inherit',
          fontSize: 11,
        }}
      >
        {events.map((e, i) => (
          <Box key={i} sx={{ mb: 0.5 }}>
            <span style={{ color: EVENT_COLOR[e.type] ?? 'rgba(255,255,255,0.5)', marginRight: 8 }}>
              [{e.type}]
            </span>
            {e.node && (
              <span style={{ color: 'rgba(255,255,255,0.4)', marginRight: 8 }}>
                {e.node}
              </span>
            )}
            <span style={{ color: 'rgba(255,255,255,0.7)' }}>{e.message ?? ''}</span>
          </Box>
        ))}
        <div ref={bottomRef} />
      </Box>
    </Drawer>
  );
}
