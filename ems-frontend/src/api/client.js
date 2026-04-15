// axios is a popular library for making HTTP requests (fetching/sending data to a server)
import axios from 'axios'

// Create a pre-configured axios instance so every API call shares the same base settings.
// Think of this as a "template" for all requests — you set it up once and reuse it everywhere.
const apiClient = axios.create({
  // baseURL is the common prefix for all requests (e.g. "http://localhost:8000").
  // The value comes from the .env file (VITE_API_BASE_URL) so it can differ
  // between development and production without changing any code.
  baseURL: import.meta.env.VITE_API_BASE_URL,

  // Tell the server we are sending JSON data in the request body
  headers: { 'Content-Type': 'application/json' }
})

// ── Request Interceptor ──────────────────────────────────────────────────────
// An interceptor is a function that runs automatically before every request is sent.
// Here we attach the user's JWT (JSON Web Token) so the backend knows who is calling.
apiClient.interceptors.request.use((config) => {
  // Retrieve the token that was saved to localStorage when the user logged in
  const token = localStorage.getItem('ems_token')

  if (token) {
    // Add the token to the Authorization header in the "Bearer" format expected by the backend
    config.headers.Authorization = `Bearer ${token}`
  }

  // Always return the (possibly modified) config so the request can continue
  return config
})

// ── Response Interceptor ─────────────────────────────────────────────────────
// This interceptor runs automatically after every response comes back from the server.
// The first callback handles successful responses; the second handles errors.
apiClient.interceptors.response.use(
  // Success path: just pass the response through unchanged
  (response) => response,

  // Error path: inspect the error before rejecting it
  (error) => {
    // HTTP 401 means "Unauthorized" — the token is missing, expired, or invalid
    if (error.response?.status === 401) {
      // Remove the stale token so the app no longer tries to use it
      localStorage.removeItem('ems_token')

      // Redirect the user to the login page so they can authenticate again
      window.location.href = '/login'
    }

    // Re-throw the error so individual API calls can still handle it if needed
    return Promise.reject(error)
  }
)

// Export the configured client so other files can import and use it for API calls
export default apiClient