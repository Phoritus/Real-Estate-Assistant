import { useContext, useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Box, Button, Container, Divider, Paper, Stack, TextField, Typography, Alert, IconButton } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { AuthContext } from '../context/AuthContext';
import LoadingIcon from '../components/LoadingIcon.tsx';
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true,
});

export default function Profile() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const user = auth?.user as any | null;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrent, setShowCurrent] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    setError(null);
    setSuccess(null);
  }, [currentPassword, newPassword, confirmPassword]);

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  const canChange = currentPassword && newPassword && confirmPassword && newPassword === confirmPassword;

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canChange) return;
    setLoading(true);
    setError(null);
    setSuccess(null);
    try {
      await axiosInstance.put('/users/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: confirmPassword,
      });
      setSuccess('Password updated successfully.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: unknown) {
      let message = 'Failed to change password';
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        const detail = (err.response?.data as any)?.detail || (err.response?.data as any)?.error || JSON.stringify(err.response?.data);
        if (status === 401) message = 'Current password is incorrect';
        else if (status) message = `Error ${status}: ${detail || 'Unexpected error'}`;
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 6, md: 8 } }}>
      <Paper elevation={8} className="glass-card soft-border fade-in" sx={{ p: { xs: 2, md: 3 }, borderRadius: 4 }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h5" fontWeight={800}>Profile</Typography>
            <Typography variant="body2" color="text.secondary">Your account details</Typography>
          </Box>

          <Paper variant="outlined" sx={{ p: 2.5, borderRadius: 3 }}>
            <Stack spacing={1}>
              <Typography variant="subtitle2" color="text.secondary">First name</Typography>
              <Typography variant="body1" fontWeight={700}>{user?.username || '-'}</Typography>
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={1}>
              <Typography variant="subtitle2" color="text.secondary">Last name</Typography>
              <Typography variant="body1" fontWeight={700}>{user?.lastname || '-'}</Typography>
            </Stack>
            <Divider sx={{ my: 2 }} />
            <Stack spacing={1}>
              <Typography variant="subtitle2" color="text.secondary">Email</Typography>
              <Typography variant="body1" fontWeight={700}>{user?.email || '-'}</Typography>
            </Stack>
          </Paper>

          <Box component="form" onSubmit={handleChangePassword} noValidate>
            <Stack spacing={2.2}>
              <Typography variant="h6" fontWeight={800}>Change password</Typography>
              <TextField
                type={showCurrent ? 'text' : 'password'}
                label="Current password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
                fullWidth
                autoComplete="current-password"
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={showCurrent ? 'Hide password' : 'Show password'}
                      onClick={() => setShowCurrent((p) => !p)}
                      edge="end"
                      size="small"
                      sx={{ color: 'text.secondary' }}
                    >
                      {showCurrent ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  ),
                }}
              />
              <TextField
                type={showNew ? 'text' : 'password'}
                label="New password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                fullWidth
                autoComplete="new-password"
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={showNew ? 'Hide password' : 'Show password'}
                      onClick={() => setShowNew((p) => !p)}
                      edge="end"
                      size="small"
                      sx={{ color: 'text.secondary' }}
                    >
                      {showNew ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  ),
                }}
              />
              <TextField
                type={showConfirm ? 'text' : 'password'}
                label="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                fullWidth
                error={Boolean(confirmPassword) && confirmPassword !== newPassword}
                helperText={Boolean(confirmPassword) && confirmPassword !== newPassword ? 'Passwords do not match' : ' '}
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={showConfirm ? 'Hide password' : 'Show password'}
                      onClick={() => setShowConfirm((p) => !p)}
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
                <Alert severity="error" sx={{ borderRadius: 2, py: 0.5 }}>{error}</Alert>
              )}
              {success && (
                <Alert severity="success" sx={{ borderRadius: 2, py: 0.5 }}>{success}</Alert>
              )}
              <Button type="submit" variant="contained" disabled={!canChange || loading} startIcon={loading ? <LoadingIcon size={20} /> : null}>
                {loading ? 'Updating…' : 'Update password'}
              </Button>
            </Stack>
          </Box>
        </Stack>
      </Paper>
    </Container>
  );
}
