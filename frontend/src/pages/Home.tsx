import { Box, Button, Container, Paper, Stack, Typography, Chip } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import EstateLogo from '../assets/estate.svg';

export default function Home() {
  return (
    <Container maxWidth="lg" sx={{ py: { xs: 6, md: 10 } }}>
      <Stack spacing={8}>
        {/* Hero Section */}
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={6} alignItems="center">
          <Box sx={{ flex: 1, textAlign: { xs: 'center', md: 'left' } }}>
            <Chip label="AI Powered" color="secondary" variant="outlined" sx={{ mb: 2, fontWeight: 600 }} />
            <Typography variant="h3" fontWeight={800} gutterBottom className="text-amber-100" sx={{ lineHeight: 1.1 }}>
              Real Estate Assistant
            </Typography>
            <Typography variant="h6" color="text.secondary" sx={{ mb: 3, maxWidth: 620, mx: { xs: 'auto', md: 0 } }}>
              Turn property links into clear, actionable insights. Compare listings, extract key facts, and ask natural questions about location, price, features and more.
            </Typography>
            <Stack direction="row" spacing={2} justifyContent={{ xs: 'center', md: 'flex-start' }}>
              <Button component={RouterLink} to="/login" size="large" variant="contained" sx={{ px: 4 }}>
                Get Started
              </Button>
              <Button component={RouterLink} to="/function" size="large" variant="outlined">
                Try the Tool
              </Button>
            </Stack>
          </Box>
          <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
            <Paper elevation={8} className="glass-card soft-border" sx={{ p: 4, borderRadius: 6, backdropFilter: 'blur(18px)', maxWidth: 340 }}>
              <Box component="img" src={EstateLogo} alt="Real Estate Assistant Logo" sx={{ width: '100%', height: 'auto', mb: 2 }} />
              <Typography variant="subtitle2" color="text.secondary" sx={{ textAlign: 'center' }}>
                Intelligent property insight engine
              </Typography>
            </Paper>
          </Box>
        </Stack>

        {/* Feature Grid (CSS Grid for stability) */}
        {(() => {
          type Feature = { title: string; desc: string; icon: string; color: string };
          const features: Feature[] = [
            { title: 'Multi-Source Parsing', desc: 'Combine up to 3 URLs for richer context.', icon: '🔗', color: 'primary.main' },
            { title: 'Smart Summaries', desc: 'Condensed answers with key points.', icon: '🧠', color: 'secondary.main' },
            { title: 'Source Transparency', desc: 'Clickable reference chips for every reply.', icon: '📚', color: 'info.main' },
            { title: 'RAG Ready', desc: 'Plug in a backend to power deep retrieval.', icon: '⚙️', color: 'success.main' },
            { title: 'Fast Mock Mode', desc: 'Use immediately while backend is in progress.', icon: '⚡', color: 'warning.main' },
            { title: 'Clean Dark UI', desc: 'Streamlit-inspired glass aesthetic.', icon: '🎨', color: 'secondary.main' },
          ];
          return (
            <Box sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' },
              gap: { xs: 2.5, sm: 3, md: 4 },
            }}>
              {features.map((f) => (
                <Paper
                  key={f.title}
                  className="glass-card soft-border"
                  sx={{ p: 3.25, display: 'flex', gap: 2.25, alignItems: 'flex-start', borderRadius: 4, position: 'relative', overflow: 'hidden',
                    '&:hover': { boxShadow: '0 8px 28px -6px rgba(0,0,0,0.55)', transform: 'translateY(-3px)', transition: 'all .35s ease' },
                  }}
                >
                  <Box aria-hidden sx={{ width: 46, height: 46, borderRadius: 3, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.35rem', bgcolor: 'rgba(255,255,255,0.07)', color: f.color, flexShrink: 0 }}>
                    {f.icon}
                  </Box>
                  <Stack spacing={0.75} sx={{ pr: 0.5 }}>
                    <Typography variant="subtitle1" fontWeight={800}>{f.title}</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.55 }}>{f.desc}</Typography>
                  </Stack>
                </Paper>
              ))}
            </Box>
          );
        })()}

        {/* How it works */}
        <Paper elevation={6} className="glass-card soft-border" sx={{ p: { xs: 3, md: 5 } }}>
          <Typography variant="h5" fontWeight={700} gutterBottom>
            How it works
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' }, gap: { xs: 2.5, sm: 3, md: 4 } }}>
            {[
              { step: '1', label: 'Gather Links', text: 'Copy up to three property / news / blog URLs.' },
              { step: '2', label: 'Ask', text: 'Type a natural language question — pricing, features, location, risks.' },
              { step: '3', label: 'Review', text: 'Read the synthesized answer with referenced sources.' },
              { step: '4', label: 'Integrate', text: 'Swap mock logic for your backend (LLM + RAG).' },
            ].map((s) => (
              <Stack key={s.step} spacing={1.2}>
                <Box sx={{ width: 40, height: 40, borderRadius: '50%', bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>
                  {s.step}
                </Box>
                <Typography variant="subtitle1" fontWeight={700}>{s.label}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.5 }}>{s.text}</Typography>
              </Stack>
            ))}
          </Box>
        </Paper>

        {/* CTA Footer */}
        <Paper elevation={4} className="glass-card soft-border" sx={{ p: { xs: 3, md: 5 }, textAlign: 'center' }}>
          <Typography variant="h5" fontWeight={800} gutterBottom>
            Ready to explore?
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            Login now and transform raw listing URLs into structured insight.
          </Typography>
          <Stack direction="row" spacing={2} justifyContent="center">
            <Button component={RouterLink} to="/login" variant="contained" size="large" sx={{ px: 5 }}>
              Login
            </Button>
            <Button component={RouterLink} to="/function" variant="outlined" size="large">
              Skip to Tool
            </Button>
          </Stack>
        </Paper>
      </Stack>
    </Container>
  );
}
