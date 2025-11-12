import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Navigate, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Container, IconButton, Paper, Stack, Switch, TextField, Typography, FormControlLabel, Divider } from '@mui/material';
import FacebookIcon from '@mui/icons-material/Facebook';
import GitHubIcon from '@mui/icons-material/GitHub';
import GoogleIcon from '@mui/icons-material/Google';
import LoadingIcon from '../components/LoadingIcon.tsx';

export default function Login() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const login = auth?.login ?? (async () => {});
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [remember, setRemember] = useState(true);

  if (isAuthenticated) return <Navigate to="/function" replace />;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await login(email, password);
    // Demo only: login() persists to localStorage regardless of remember
    setLoading(false);
    navigate('/function');
  };

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 6, md: 8 } }}>
      <Paper elevation={8} className="glass-card soft-border fade-in" sx={{ p: { xs: 2, md: 3 }, borderRadius: 4 }}>
        <Stack spacing={3}>
          {/* Header with gradient */}
          <Box sx={{
            textAlign: 'center',
            p: 3,
            borderRadius: 3,
            background: 'linear-gradient(135deg, #0070f3 0%, #6f5ef9 50%, #5f9df7 100%)',
            color: 'white',
            boxShadow: '0 10px 26px -12px rgba(0,0,0,0.6)'
          }}>
            <Typography variant="h5" fontWeight={800}>Sign in</Typography>
            <Stack direction="row" spacing={3} justifyContent="center" sx={{ mt: 2 }}>
              <IconButton color="inherit" size="large" aria-label="Sign in with Facebook"><FacebookIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign in with GitHub"><GitHubIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign in with Google"><GoogleIcon sx={{ color: 'white' }} /></IconButton>
            </Stack>
          </Box>

          {/* Form */}
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Stack spacing={2.2}>
              <TextField
                type="email"
                label="Email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                fullWidth
              />
              <TextField
                type="password"
                label="Password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
              />
              <FormControlLabel
                control={<Switch checked={remember} onChange={(e) => setRemember(e.target.checked)} />}
                label={<Typography color="text.secondary">Remember me</Typography>}
              />
              <Button type="submit" variant="contained" disabled={loading} sx={{ py: 1.25, fontWeight: 700 }} startIcon={loading ? <LoadingIcon size={20} /> : null}>
                {loading ? 'Signing in…' : 'Sign in'}
              </Button>
            </Stack>
          </Box>

          <Divider sx={{ opacity: 0.3 }} />

          <Typography variant="body2" color="text.secondary" textAlign="center">
            Don't have an account?{' '}
            <Button component={RouterLink} to="/signup" variant="text" size="small">Sign up</Button>
          </Typography>
        </Stack>
      </Paper>
    </Container>
  );
}
