import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Navigate, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Container, IconButton, Paper, Stack, Switch, TextField, Typography, FormControlLabel, Divider, Alert } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import FacebookIcon from '@mui/icons-material/Facebook';
import GitHubIcon from '@mui/icons-material/GitHub';
import GoogleIcon from '@mui/icons-material/Google';
import LoadingIcon from '../components/LoadingIcon.tsx';
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
});

export default function SignUp() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const login = auth?.login ?? (async () => {});
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [username, setUsername] = useState('');
  const [lastname, setLastname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [updates, setUpdates] = useState(true);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) return <Navigate to="/function" replace />;

  const canSubmit = username && lastname && email && password && confirm && password === confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    try {
      await axiosInstance.post('/auth/register', {
        username,
        lastname,
        email,
        password,
      });
      // Optionally auto-login, but safer to redirect to login
      navigate('/login');
    } catch (err) {
      let message = 'Sign up failed';
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const detail = (err.response?.data as any)?.detail || (err.response?.data as any)?.error || JSON.stringify(err.response?.data);
        if (status === 409) message = 'Email already in use';
        else if (status) message = `Error ${status}: ${detail || 'Unexpected error'}`;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const oauthLoginGoogle = async () => {
    try {
      const response = await axiosInstance.get('/auth/google-login-url');
      const { url } = response.data;
      window.location.href = url;
    } catch (e) {
      setError('Could not connect to Google Sign-In.');
    }
  };

  const oauthLoginFacebook = async () => {
    try {
      const response = await axiosInstance.get('/auth/facebook-login-url');
      const { url } = response.data;
      window.location.href = url;
    } catch (e) {
      setError('Could not connect to Facebook Sign-In.');
    }
  };

  const oauthLoginGitHub = async () => {
    try {
      const response = await axiosInstance.get('/auth/github-login-url');
      const { url } = response.data;
      window.location.href = url;
    } catch (e) {
      setError('Could not connect to GitHub Sign-In.');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 6, md: 8 } }}>
      <Paper elevation={8} className="glass-card soft-border fade-in" sx={{ p: { xs: 2, md: 3 }, borderRadius: 4 }}>
        <Stack spacing={3}>
          <Box sx={{
            textAlign: 'center', p: 3, borderRadius: 3,
            background: 'linear-gradient(135deg, #6f5ef9 0%, #0070f3 55%, #51b3ff 100%)',
            color: 'white', boxShadow: '0 10px 26px -12px rgba(0,0,0,0.6)'
          }}>
            <Typography variant="h5" fontWeight={800}>Create account</Typography>
            <Stack direction="row" spacing={3} justifyContent="center" sx={{ mt: 2 }}>
              <IconButton color="inherit" size="large" aria-label="Sign up with Facebook" onClick={oauthLoginFacebook}><FacebookIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign up with GitHub" onClick={oauthLoginGitHub}><GitHubIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign up with Google" onClick={oauthLoginGoogle}><GoogleIcon sx={{ color: 'white' }} /></IconButton>
            </Stack>
          </Box>

          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Stack spacing={2.2}>
              <TextField
                type="text"
                label="First name"
                placeholder="John"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                fullWidth
                autoComplete="given-name"
              />
              <TextField
                type="text"
                label="Last name"
                placeholder="Doe"
                value={lastname}
                onChange={(e) => setLastname(e.target.value)}
                required
                fullWidth
                autoComplete="family-name"
              />
              <TextField
                type="email"
                label="Email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                fullWidth
                autoComplete="email"
              />
              <TextField
                type={showPassword ? 'text' : 'password'}
                label="Password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
                autoComplete="new-password"
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      onClick={() => setShowPassword((prev) => !prev)}
                      edge="end"
                      size="small"
                      sx={{ color: 'text.secondary' }}
                    >
                      {showPassword ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  ),
                }}
              />
              <TextField
                type={showConfirm ? 'text' : 'password'}
                label="Confirm Password"
                placeholder="Repeat password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                fullWidth
                error={Boolean(confirm) && confirm !== password}
                helperText={Boolean(confirm) && confirm !== password ? 'Passwords do not match' : ' '}
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={showConfirm ? 'Hide password' : 'Show password'}
                      onClick={() => setShowConfirm((prev) => !prev)}
                      edge="end"
                      size="small"
                      sx={{ color: 'text.secondary' }}
                    >
                      {showConfirm ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  ),
                }}
              />
              {error && (
                <Alert severity="error" sx={{ borderRadius: 2, py: 0.5 }}>
                  {error}
                </Alert>
              )}
              <FormControlLabel
                control={<Switch checked={updates} onChange={(e) => setUpdates(e.target.checked)} />}
                label={<Typography color="text.secondary">Email me product updates</Typography>}
              />
              <Button type="submit" variant="contained" disabled={!canSubmit || loading} sx={{ py: 1.25, fontWeight: 700 }} startIcon={loading ? <LoadingIcon size={20} /> : null}>
                {loading ? 'Creating…' : 'Sign up'}
              </Button>
            </Stack>
          </Box>

          <Divider sx={{ opacity: 0.3 }} />

          <Typography variant="body2" color="text.secondary" textAlign="center">
            Already have an account?{' '}
            <Button component={RouterLink} to="/login" variant="text" size="small">Sign in</Button>
          </Typography>
        </Stack>
      </Paper>
    </Container>
  );
}
