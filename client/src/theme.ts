import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0d0d0d',
      paper: '#1a1a1a',
    },
    primary: {
      main: '#4a9eff',
    },
    secondary: {
      main: '#ff6b6b',
    },
    divider: 'rgba(255,255,255,0.08)',
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Fira Code", "Consolas", monospace',
    fontSize: 13,
    h6: { fontWeight: 600, letterSpacing: 0.5 },
    body1: { fontSize: 13 },
    body2: { fontSize: 12 },
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          minWidth: 120,
          fontWeight: 500,
          letterSpacing: 0.5,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 500 },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontFamily: 'inherit' },
      },
    },
  },
});
