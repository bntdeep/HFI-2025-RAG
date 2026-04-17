import { useEffect, useRef, useState } from 'react';
import {
  Box,
  CircularProgress,
  Divider,
  IconButton,
  InputAdornment,
  Paper,
  Stack,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useChatStore } from '../store/chatStore.js';
import { SourcesList } from './SourcesList.js';

export function ChatTab() {
  const { messages, isLoading, error, sendMessage, clearChat } = useChatStore();
  const [input, setInput] = useState('');
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const submit = () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');
    sendMessage(text);
  };

  return (
    <Stack sx={{ height: 'calc(100vh - 160px)', minHeight: 400 }} spacing={0}>
      {/* Messages area */}
      <Box sx={{ flex: 1, overflowY: 'auto', pb: 2, pr: 1 }}>
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 8, color: 'text.secondary' }}>
            <Typography variant="body2">
              Ask anything about the 2025 Human Freedom Index
            </Typography>
            <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.6 }}>
              e.g. "What is Norway's rule of law score?" · "Compare top 5 countries by personal freedom"
            </Typography>
          </Box>
        )}

        {messages.map(msg => (
          <Box key={msg.id} sx={{ mb: 2 }}>
            <Typography
              variant="caption"
              sx={{
                display: 'block',
                mb: 0.5,
                color: msg.role === 'user' ? 'primary.main' : 'text.secondary',
                textTransform: 'uppercase',
                letterSpacing: 1,
              }}
            >
              {msg.role === 'user' ? 'You' : 'HFI Assistant'}
            </Typography>

            {msg.role === 'user' ? (
              <Paper sx={{ p: 1.5, bgcolor: 'rgba(74,158,255,0.07)', border: '1px solid rgba(74,158,255,0.15)' }}>
                <Typography variant="body2">{msg.content}</Typography>
              </Paper>
            ) : (
              <Paper sx={{ p: 1.5 }}>
                <Box sx={{ '& p': { mt: 0.5, mb: 0.5 }, '& code': { bgcolor: 'rgba(255,255,255,0.06)', px: 0.5, borderRadius: 0.5, fontFamily: 'inherit', fontSize: 12 }, '& pre': { bgcolor: 'rgba(255,255,255,0.04)', p: 1, borderRadius: 1, overflowX: 'auto' }, '& table': { borderCollapse: 'collapse', width: '100%' }, '& td,& th': { border: '1px solid rgba(255,255,255,0.1)', px: 1, py: 0.5, fontSize: 12 } }}>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </Box>
                {msg.sources && msg.sources.length > 0 && (
                  <>
                    <Divider sx={{ my: 1 }} />
                    <SourcesList sources={msg.sources} compact />
                  </>
                )}
              </Paper>
            )}
          </Box>
        ))}

        {isLoading && (
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', color: 'text.secondary', mb: 1 }}>
            <CircularProgress size={14} />
            <Typography variant="caption">Searching HFI data…</Typography>
          </Stack>
        )}

        {error && (
          <Typography color="error" variant="caption">{error}</Typography>
        )}

        <div ref={bottomRef} />
      </Box>

      {/* Input */}
      <Paper sx={{ p: 1.5, mt: 'auto' }}>
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            size="small"
            placeholder="Ask about freedom indices, rankings, or country comparisons…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submit();
              }
            }}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={submit} disabled={!input.trim() || isLoading}>
                      <SendIcon fontSize="small" />
                    </IconButton>
                  </InputAdornment>
                ),
              },
            }}
          />
          <Tooltip title="Clear chat">
            <IconButton size="small" onClick={clearChat}>
              <DeleteOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Stack>
      </Paper>
    </Stack>
  );
}
