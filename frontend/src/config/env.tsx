// Use Vite's environment variables. Do NOT use process.env in browser code.
// Define `VITE_API_BASE_URL` in your frontend .env files (e.g., .env, .env.development)
// Example:
// VITE_API_BASE_URL=http://localhost:8000

export const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';