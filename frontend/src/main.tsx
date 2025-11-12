import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: { default: '#0E1117', paper: 'rgba(22,27,34,0.85)' },
    primary: { main: '#0070f3' },
    secondary: { main: '#6f5ef9' },
    info: { main: '#ff6ec7' },
    success: { main: '#1db954' },
  },
  shape: { borderRadius: 14 },
  typography: {
    fontFamily: 'Plus Jakarta Sans, Roboto, sans-serif',
    h4: { fontWeight: 800, letterSpacing: '-0.5px' },
    h6: { fontWeight: 700 },
    button: { fontWeight: 600 },
  },
  components: {
    MuiPaper: { styleOverrides: { root: { backgroundImage: 'none' } } },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 14,
          transition: 'all .25s ease',
        },
        containedPrimary: {
          background: 'linear-gradient(135deg,#0070f3 0%, #6f5ef9 60%)',
          boxShadow: '0 4px 18px -4px rgba(0,112,243,0.55)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': { borderRadius: 14 },
        },
      },
    },
    MuiChip: { styleOverrides: { root: { fontWeight: 600 } } },
  },
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </StrictMode>
);
