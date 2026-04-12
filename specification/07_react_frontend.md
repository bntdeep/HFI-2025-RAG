## 7. React Frontend

7.1 Layout



┌─────────────────────────────────────────────────────────────────┐
│  Header: "Human Freedom Index Analyzer"    [📄 Documents]       │
├────────────────────────────────┬────────────────────────────────┤
│          MAIN PANEL (60%)      │      DEBUG CONSOLE (40%)       │
│                                │                                │
│  ┌──────────────────────────┐  │  ┌──────────────────────────┐ │
│  │  Mode Toggle:            │  │  │  [Clear] [Pause] [Auto]  │ │
│  │  [💬 Chat] [📊 Compare]  │  │  │                          │ │
│  └──────────────────────────┘  │  │  12:03:01 [MCP] call     │ │
│                                │  │    tool: search_documents │ │
│  === IF COMPARE MODE ===       │  │    query: "Switzerland"   │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │ Countries:               │  │  │  12:03:01 [Retriever]    │ │
│  │ [🇨🇭 Switzerland ▼]      │  │  │    chunks: 5             │ │
│  │ [🇯🇵 Japan        ▼]      │  │  │    top_score: 0.89      │ │
│  │ [+ Add country]          │  │  │                          │ │
│  │                          │  │  │  12:03:02 [LLM] request  │ │
│  │ Parameters:              │  │  │    model: gpt-4.1        │ │
│  │ ☑ Personal Freedom       │  │  │    tokens: 1847          │ │
│  │ ☑ Economic Freedom       │  │  │                          │ │
│  │ ☐ Rule of Law            │  │  │  12:03:03 [LLM] response │ │
│  │ ☐ Security & Safety      │  │  │    tokens: 423           │ │
│  │ ...                      │  │  │    duration: 1.2s        │ │
│  │                          │  │  │                          │ │
│  │ [🔍 Compare]             │  │  │  12:03:03 [Chart] ready  │ │
│  └──────────────────────────┘  │  │    type: bar             │ │
│                                │  │    points: 2             │ │
│  === CHART AREA ===            │  │                          │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │                          │  │  │                          │ │
│  │   [Recharts Bar/Pie/etc] │  │  │                          │ │
│  │                          │  │  │                          │ │
│  └──────────────────────────┘  │  │                          │ │
│                                │  │                          │ │
│  === ANALYSIS TEXT ===         │  │                          │ │
│  ┌──────────────────────────┐  │  │                          │ │
│  │ Switzerland scores higher│  │  │                          │ │
│  │ in personal freedom by...│  │  │                          │ │
│  │ Sources: p.42, p.67      │  │  │                          │ │
│  └──────────────────────────┘  │  │                          │ │
│                                │  │                          │ │
│  === IF CHAT MODE ===          │  └──────────────────────────┘ │
│  ┌──────────────────────────┐  │                                │
│  │ Chat messages...          │  │                                │
│  │ [Type message...] [Send] │  │                                │
│  └──────────────────────────┘  │                                │
├────────────────────────────────┴────────────────────────────────┤
│  Footer: Connected ● | Docs: 1 | Chunks: 347                   │
└─────────────────────────────────────────────────────────────────┘
7.2 Documents Modal



┌─────────────────────────────────────────────┐
│  📄 Indexed Documents                  [✕]  │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │ 📕 2025-human-freedom-index.pdf     │    │
│  │    Pages: 98 | Chunks: 347          │    │
│  │    Uploaded: 2025-01-15 14:30       │    │
│  │    Size: 4.2 MB                     │    │
│  │                          [🗑 Delete] │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┐    │
│  │   Drag & drop PDF here              │    │
│  │   or [Browse Files]                 │    │
│  └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┘    │
│                                             │
│  ⏳ Processing: analyzing tables... (43%)   │
│                                             │
└─────────────────────────────────────────────┘
7.3 Theme (Grayscale Minimalist)

javascript


// MUI theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#ffffff' },
    secondary: { main: '#9e9e9e' },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#e0e0e0',
      secondary: '#9e9e9e',
    },
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Fira Code", monospace',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 2,
          textTransform: 'none',
        },
      },
    },
  },
});

// Chart colors (grayscale with one accent)
const CHART_COLORS = [
  '#e0e0e0', // white-ish
  '#9e9e9e', // medium gray  
  '#616161', // dark gray
  '#424242', // darker
  '#bdbdbd', // light gray
  '#757575', // mid
];
7.4 Component Tree



App
├── Header
│   ├── Logo + Title
│   ├── ConnectionStatus (● Connected)
│   └── DocumentsButton → DocumentsModal
├── MainLayout (split horizontal)
│   ├── MainPanel (left 60%)
│   │   ├── ModeToggle (Chat | Compare)
│   │   ├── ComparePanel (if compare mode)
│   │   │   ├── CountrySelector (multi-select dropdown with flags)
│   │   │   ├── ParameterPicker (checkboxes)
│   │   │   └── CompareButton
│   │   ├── ChatPanel (if chat mode)
│   │   │   ├── MessageList (streaming messages)
│   │   │   └── MessageInput
│   │   ├── ChartArea
│   │   │   └── DynamicChart (renders based on chart_config)
│   │   ├── AnalysisText (markdown rendered)
│   │   └── SourceReferences (collapsible)
│   └── DebugConsole (right 40%)
│       ├── ConsoleToolbar (Clear | Pause | AutoScroll)
│       └── EventList (virtualized scroll)
│           └── DebugEvent (color-coded by type)
├── DocumentsModal
│   ├── DocumentList
│   │   └── DocumentCard (name, stats, delete)
│   └── UploadArea (drag & drop + progress)
└── Footer
    └── Stats (docs count, chunks count, connection)
