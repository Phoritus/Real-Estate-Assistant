import { useState, useContext, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate, Navigate, Link as RouterLink } from "react-router-dom";
import {
  Box,
  Button,
  Container,
  IconButton,
  Paper,
  Stack,
  Switch,
  TextField,
  Typography,
  FormControlLabel,
  Divider,
  Alert,
} from "@mui/material";
import FacebookIcon from "@mui/icons-material/Facebook";
import GitHubIcon from "@mui/icons-material/GitHub";
import GoogleIcon from "@mui/icons-material/Google";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import LoadingIcon from "../components/LoadingIcon.tsx";
import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000",
  withCredentials: true,
});

export default function Login() {
  const auth = useContext(AuthContext);
  const isAuthenticated = Boolean(auth?.isAuthenticated);
  const login = auth?.login ?? (async () => {});
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  if (isAuthenticated) return <Navigate to="/function" replace />;

  const oauthLoginGoogle = async () => {
    try {
      const response = await axiosInstance.get("/auth/google-login-url");
      const { url } = response.data;
      window.location.href = url;
    } catch (error) {
      console.error("Failed to get Google login URL", error);
      setLoginError("Could not connect to Google Sign-In.");
    }
  };

  const oauthLoginFacebook = async () => {
    try {
      const response = await axiosInstance.get("/auth/facebook-login-url");
      const { url } = response.data;
      window.location.href = url;
    } catch (error) {
      console.error("Failed to get Facebook login URL", error);
      setLoginError("Could not connect to Facebook Sign-In.");
    }
  };

  const oauthLoginGitHub = async () => {
    try {
      const response = await axiosInstance.get("/auth/github-login-url");
      const { url } = response.data;
      window.location.href = url;
    } catch (error) {
      console.error("Failed to get GitHub login URL", error);
      setLoginError("Could not connect to GitHub Sign-In.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoginError(null);

    const formDetails = new URLSearchParams();
    formDetails.append("grant_type", "password");
    formDetails.append("username", email);
    formDetails.append("password", password);
    formDetails.append("remember", remember ? "true" : "false");

    try {
      const response = await axiosInstance.post("/auth/login", formDetails);

      const authToken = response.data;
      await login(authToken);
      navigate("/function");
    } catch (error) {
      let message = "Login failed";
      if (axios.isAxiosError(error)) {
        const status = error.response?.status;
        const detail = (error.response?.data as any)?.detail;
        if (status === 401 || status === 400)
          message = detail || "Invalid email or password";
        else if (status)
          message = `Error ${status}: ${detail || "Unexpected error"}`;
      } else if (error instanceof Error) {
        message = error.message;
      }
      setLoginError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 6, md: 8 } }}>
      <Paper
        elevation={8}
        className="glass-card soft-border fade-in"
        sx={{ p: { xs: 2, md: 3 }, borderRadius: 4 }}
      >
        <Stack spacing={3}>
          {/* Header with gradient */}
          <Box
            sx={{
              textAlign: "center",
              p: 3,
              borderRadius: 3,
              background:
                "linear-gradient(135deg, #0070f3 0%, #6f5ef9 50%, #5f9df7 100%)",
              color: "white",
              boxShadow: "0 10px 26px -12px rgba(0,0,0,0.6)",
            }}
          >
            <Typography variant="h5" fontWeight={800}>
              Sign in
            </Typography>
            <Stack
              direction="row"
              spacing={3}
              justifyContent="center"
              sx={{ mt: 2 }}
            >
              <IconButton
                color="inherit"
                size="large"
                aria-label="Sign in with Facebook"
                onClick={oauthLoginFacebook}
              >
                <FacebookIcon sx={{ color: "white" }} />
              </IconButton>
              <IconButton
                color="inherit"
                size="large"
                aria-label="Sign in with GitHub"
                onClick={oauthLoginGitHub}
              >
                <GitHubIcon sx={{ color: "white" }} />
              </IconButton>
              <IconButton
                color="inherit"
                size="large"
                aria-label="Sign in with Google"
                onClick={oauthLoginGoogle}
              >
                <GoogleIcon sx={{ color: "white" }} />
              </IconButton>
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
                autoComplete="email"
              />
              <TextField
                type={showPassword ? "text" : "password"}
                label="Password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                fullWidth
                autoComplete="current-password"
                error={Boolean(loginError)}
                helperText={loginError || ""}
                InputProps={{
                  endAdornment: (
                    <IconButton
                      aria-label={
                        showPassword ? "Hide password" : "Show password"
                      }
                      onClick={() => setShowPassword((prev) => !prev)}
                      edge="end"
                      size="small"
                      sx={{ color: "text.secondary" }}
                    >
                      {showPassword ? <Visibility /> : <VisibilityOff />}
                    </IconButton>
                  ),
                }}
              />
              {loginError && (
                <Alert severity="error" sx={{ borderRadius: 2, py: 0.5 }}>
                  {loginError}
                </Alert>
              )}
              <FormControlLabel
                control={
                  <Switch
                    checked={remember}
                    onChange={(e) => setRemember(e.target.checked)}
                  />
                }
                label={
                  <Typography color="text.secondary">Remember me</Typography>
                }
              />
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                sx={{ py: 1.25, fontWeight: 700 }}
                startIcon={loading ? <LoadingIcon size={20} /> : null}
              >
                {loading ? "Signing in…" : "Sign in"}
              </Button>
            </Stack>
          </Box>

          <Divider sx={{ opacity: 0.3 }} />

          <Typography variant="body2" color="text.secondary" textAlign="center">
            Don't have an account?{" "}
            <Button
              component={RouterLink}
              to="/signup"
              variant="text"
              size="small"
            >
              Sign up
            </Button>
          </Typography>
        </Stack>
      </Paper>
    </Container>
  );
}
