import { useEffect, useState } from 'react';
import {
  AppBar,
  Box,
  Container,
  CssBaseline,
  IconButton,
  Stack,
  Tab,
  Tabs,
  ThemeProvider,
  Toolbar,
  Tooltip,
  Typography,
} from '@mui/material';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import BugReportOutlinedIcon from '@mui/icons-material/BugReportOutlined';
import BalanceIcon from '@mui/icons-material/Balance';
import { theme } from './theme.js';
import { useMetaStore } from './store/metaStore.js';
import { useDebugStore } from './store/debugStore.js';
import { useWebSocket } from './hooks/useWebSocket.js';
import { CompareTab } from './components/CompareTab.js';
import { CountryTab } from './components/CountryTab.js';
import { ChatTab } from './components/ChatTab.js';
import { DebugConsole } from './components/DebugConsole.js';
import { DocumentsModal } from './components/DocumentsModal.js';

function App() {
  const [tab, setTab] = useState(0);
  const [docsOpen, setDocsOpen] = useState(false);
  const load = useMetaStore(s => s.load);
  const toggleDebug = useDebugStore(s => s.toggle);

  useWebSocket();

  useEffect(() => {
    load();
  }, [load]);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />

      <AppBar position="sticky" elevation={0} sx={{ borderBottom: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
        <Toolbar variant="dense" sx={{ minHeight: 48 }}>
          {/* Logo */}
          <Stack direction="row" spacing={1} sx={{ alignItems: 'center', mr: 3 }}>
            <BalanceIcon sx={{ color: 'primary.main', fontSize: 20 }} />
            <Typography variant="h6" sx={{ fontSize: 14, fontWeight: 700, letterSpacing: 1 }}>
              HFI&nbsp;<Typography component="span" variant="h6" sx={{ fontSize: 14, fontWeight: 400, color: 'text.secondary' }}>2025</Typography>
            </Typography>
          </Stack>

          {/* Tabs */}
          <Tabs
            value={tab}
            onChange={(_, v) => setTab(v)}
            sx={{ flex: 1, '& .MuiTabs-indicator': { height: 2 } }}
          >
            <Tab label="Compare" />
            <Tab label="Country" />
            <Tab label="Chat" />
          </Tabs>

          {/* Actions */}
          <Tooltip title="Documents">
            <IconButton size="small" onClick={() => setDocsOpen(true)}>
              <FolderOpenIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Debug console">
            <IconButton size="small" onClick={toggleDebug} sx={{ ml: 0.5 }}>
              <BugReportOutlinedIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ pt: 3, pb: 6 }}>
        <Box hidden={tab !== 0}><CompareTab /></Box>
        <Box hidden={tab !== 1}><CountryTab /></Box>
        <Box hidden={tab !== 2}><ChatTab /></Box>
      </Container>

      <DebugConsole />
      <DocumentsModal open={docsOpen} onClose={() => setDocsOpen(false)} />
    </ThemeProvider>
  );
}

export default App;
