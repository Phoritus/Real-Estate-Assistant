import { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { useNavigate, Navigate, Link as RouterLink } from 'react-router-dom';
import { Box, Button, Container, IconButton, Paper, Stack, Switch, TextField, Typography, FormControlLabel, Divider } from '@mui/material';
import FacebookIcon from '@mui/icons-material/Facebook';
import GitHubIcon from '@mui/icons-material/GitHub';
import GoogleIcon from '@mui/icons-material/Google';
import LoadingIcon from '../components/LoadingIcon.tsx';

export default function SignUp() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const login = auth?.login ?? (async () => {});
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [updates, setUpdates] = useState(true);

  if (isAuthenticated) return <Navigate to="/function" replace />;

  const canSubmit = email && password && confirm && password === confirm;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSubmit) return;
    setLoading(true);
    // Demo: reuse login once "registered"
    await login(email, password);
    setLoading(false);
    navigate('/function');
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
              <IconButton color="inherit" size="large" aria-label="Sign up with Facebook"><FacebookIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign up with GitHub"><GitHubIcon sx={{ color: 'white' }} /></IconButton>
              <IconButton color="inherit" size="large" aria-label="Sign up with Google"><GoogleIcon sx={{ color: 'white' }} /></IconButton>
            </Stack>
          </Box>

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
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
              />
              <TextField
                type="password"
                label="Confirm Password"
                placeholder="Repeat password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                fullWidth
                error={Boolean(confirm) && confirm !== password}
                helperText={Boolean(confirm) && confirm !== password ? 'Passwords do not match' : ' '}
              />
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
