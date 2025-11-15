import { useMemo, useState, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link as RouterLink, useNavigate } from 'react-router-dom';
import { AppBar, Toolbar, Button, Chip, Container, LinearProgress, Paper, Stack, TextField, Typography, Box, Backdrop, CircularProgress } from '@mui/material';
import './index.css';
import Home from './pages/Home.tsx';
import Login from './pages/Login.tsx';
import SignUp from './pages/SignUp.tsx';
import Profile from './pages/Profile.tsx';
import { ProtectedRoute } from './components/ProtectedRoute.tsx';
import { AuthProvider, AuthContext } from './context/AuthContext.tsx';
import LoadingIcon from './components/LoadingIcon.tsx';
import axios from 'axios';


// Keep validators
const isValidUrl = (value: string) => {
  if (!value) return false;
  try { const u = new URL(value); return u.protocol === 'http:' || u.protocol === 'https:'; } catch { return false; }
};
const getDomain = (url: string) => { try { const u = new URL(url); return u.hostname.replace(/^www\./, ''); } catch { return 'source'; } };

function FunctionPage() {
  const [url1, setUrl1] = useState('');
  const [url2, setUrl2] = useState('');
  const [url3, setUrl3] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<string[]>([]);

  const urls = useMemo(() => [url1, url2, url3].filter(Boolean), [url1, url2, url3]);

  const canSubmit = useMemo(() => {
    if (!question.trim()) return false;
    if (urls.length === 0) return false;
    // require all provided urls to be valid
    return urls.every(isValidUrl);
  }, [urls, question]);

  const handleProcess = async () => {
    setError(null);
    setAnswer('');
    setSources([]);

    const provided = [url1, url2, url3].filter(Boolean);
    if (provided.length === 0) {
      setError('Please provide at least 1 URL');
      return;
    }
    if (!question.trim()) {
      setError('Please enter your question');
      return;
    }
    if (!provided.every(isValidUrl)) {
      setError('Some URLs look invalid (must start with http/https).');
      return;
    }

    const axiosInstance = axios.create({
      baseURL: 'http://localhost:8000',
      withCredentials: true,
    });

    setLoading(true);
    try {
      // 1) Process URLs
      setLoadingStage('Initializing & indexing sources…');
      await axiosInstance.post('/process/process-urls', { urls: provided });

      // 2) Query answer
      setLoadingStage('Generating answer…');
      const { data } = await axiosInstance.post('/process/query', { question: question.trim() });

      setAnswer(data?.answer || 'No answer');
      const src = (data?.sources || '') as string;
      const list = src ? src.split(',').map((s: string) => s.trim()).filter(Boolean) : provided;
      setSources(list);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Unexpected error occurred';
      setError(message);
    } finally {
      setLoading(false);
      setLoadingStage(null);
    }
  };

  const handleReset = () => {
    setUrl1('');
    setUrl2('');
    setUrl3('');
    setQuestion('');
    setAnswer('');
    setSources([]);
    setError(null);
  };
  
  return (
    <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
      <Stack spacing={3} className="fade-in">
        <Box>
          <Typography variant="h4" fontWeight={800} gutterBottom sx={{ color: 'primary.main' }}>
            Real Estate Assistant 🏢✨
          </Typography>
          <Typography variant="subtitle1" sx={{ color: 'text.secondary', maxWidth: 760 }}>
            Paste up to 3 URLs and ask your question. We’ll do the rest. ✨
          </Typography>
        </Box>

        {loading && <LinearProgress color="secondary" sx={{ borderRadius: 2 }} />}

        <Paper elevation={6} className="glass-card soft-border" sx={{ p: { xs: 2.5, md: 3.5 } }}>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Data Sources (URLs) 🔗
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Add listing pages, project updates, market blog posts, review articles, etc.
              </Typography>
            </Box>
            <TextField
              label="URL 1"
              placeholder="https://portal.example.com/listing/12345"
              value={url1}
              onChange={(e) => setUrl1(e.target.value)}
              fullWidth
              helperText={url1 && !isValidUrl(url1) ? 'Invalid URL format' : 'Primary source (required)'}
              error={Boolean(url1) && !isValidUrl(url1)}
            />
            <TextField
              label="URL 2 (optional)"
              placeholder="https://blog.example.com/market-trends"
              value={url2}
              onChange={(e) => setUrl2(e.target.value)}
              fullWidth
              helperText={url2 && !isValidUrl(url2) ? 'Invalid URL format' : 'Add supporting context'}
              error={Boolean(url2) && !isValidUrl(url2)}
            />
            <TextField
              label="URL 3 (optional)"
              placeholder="https://news.example.com/project-update"
              value={url3}
              onChange={(e) => setUrl3(e.target.value)}
              fullWidth
              helperText={url3 && !isValidUrl(url3) ? 'Invalid URL format' : 'Enhance coverage'}
              error={Boolean(url3) && !isValidUrl(url3)}
            />

            <Box>
              <Typography variant="h6" fontWeight={700} gutterBottom>
                Your Question ❓
              </Typography>
              <TextField
                label="Question"
                placeholder="e.g. What are the standout features, average price per sqm, and is the location attractive?"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                fullWidth
                multiline
                minRows={3}
              />
            </Box>

            {error && (
              <Paper variant="outlined" sx={{ p: 2, borderColor: 'error.main', bgcolor: 'error.main', color: 'error.contrastText', borderRadius: 3 }}>
                <Typography variant="body2">{error} ⚠️</Typography>
              </Paper>
            )}

            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleProcess}
                disabled={!canSubmit || loading}
                startIcon={loading ? <LoadingIcon size={20} /> : null}
                sx={{
                  px: 3.5,
                  py: 1.2,
                  fontSize: '0.95rem',
                  '&:hover': {
                    boxShadow: '0 6px 22px -4px rgba(111,94,249,0.65)',
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all .3s ease',
                }}
              >
                {loading ? 'Processing…' : 'Process URLs 🚀'}
              </Button>
              <Button
                variant="outlined"
                color="inherit"
                onClick={handleReset}
                disabled={loading}
                sx={{ borderRadius: 14, '&:hover': { background: 'rgba(255,255,255,0.05)' } }}
              >
                Reset 🔄
              </Button>
            </Stack>
          </Stack>
        </Paper>

        {(answer || sources.length > 0) && (
          <Paper elevation={4} className="glass-card soft-border fade-in" sx={{ p: { xs: 2.5, md: 3.5 }, mt: 1 }}>
            <Stack spacing={3}>
              {answer && (
                <Box>
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    Answer 🧠
                  </Typography>
                  <Typography whiteSpace="pre-wrap" sx={{ lineHeight: 1.6 }}>
                    {answer}
                  </Typography>
                </Box>
              )}

              {sources.length > 0 && (
                <Box>
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    Sources 📚
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1.2}>
                    {sources.map((s, i) => (
                      <Chip
                        key={s + i}
                        label={`${getDomain(s)}`}
                        component="a"
                        href={s}
                        target="_blank"
                        rel="noopener noreferrer"
                        clickable
                        color={i % 3 === 0 ? 'primary' : i % 3 === 1 ? 'secondary' : 'info'}
                        variant="outlined"
                        sx={{
                          backdropFilter: 'blur(6px)',
                          borderRadius: 10,
                          fontSize: '0.75rem',
                          letterSpacing: 0.3,
                        }}
                      />
                    ))}
                  </Stack>
                </Box>
              )}
            </Stack>
          </Paper>
        )}
        <Backdrop open={loading} sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Stack alignItems="center" spacing={2}>
            <CircularProgress color="inherit" />
            <Typography variant="body2">{loadingStage || 'Processing…'}</Typography>
          </Stack>
        </Backdrop>
      </Stack>
    </Container>
  );
}

function NavBar() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const logout = auth?.logout ?? (() => {});
  const navigate = useNavigate();
  return (
    <AppBar position="sticky" color="transparent" elevation={0} sx={{ backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
      <Toolbar sx={{ gap: 2 }}>
        <Button component={RouterLink} to="/" color="inherit" sx={{ fontWeight: 700 }}>
          Home
        </Button>
        <Button component={RouterLink} to="/function" color="inherit" sx={{ fontWeight: 700 }}>
          Function
        </Button>
        {isAuthenticated && (
          <Button component={RouterLink} to="/profile" color="inherit" sx={{ fontWeight: 700 }}>
            Profile
          </Button>
        )}
        {!isAuthenticated && (
          <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
            <Button component={RouterLink} to="/login" color="inherit">Login</Button>
            <Button component={RouterLink} to="/signup" color="inherit">Sign up</Button>
          </Box>
        )}
        {isAuthenticated && (
          <Button onClick={async () => { await logout(); navigate('/login', { replace: true }); }} color="inherit" sx={{ ml: 'auto' }}>
            Logout
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}

function AppRoutes() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/function" element={<ProtectedRoute><FunctionPage /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
