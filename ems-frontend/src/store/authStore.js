// Zustand is a lightweight state management library.
// It lets you store data (like the logged-in user) in one place so any
// component in the app can read or update it without passing props around.
import { create } from 'zustand'

// The pre-configured axios instance that automatically attaches the JWT to requests
import apiClient from '../api/client'

// create() builds a Zustand store. The callback receives `set`, a function used
// to update pieces of the store's state.
const useAuthStore = create((set) => ({
  // The logged-in user's profile data (null means no one is logged in yet)
  user: null,

  // Try to restore the token from localStorage so the user stays logged in
  // across page refreshes. Returns null if no token was previously saved.
  token: localStorage.getItem('ems_token'),

  // Convert the token to a boolean: true if a token exists, false otherwise.
  // The !! (double-bang) is a quick way to turn any value into true/false.
  isAuthenticated: !!localStorage.getItem('ems_token'),

  // ── login ────────────────────────────────────────────────────────────────
  // Called when the user submits the login form.
  // Sends credentials to the backend and, on success, saves the JWT.
  login: async (email, password) => {
    // The backend's /auth/login endpoint expects form-encoded data, not JSON.
    // URLSearchParams formats the data as "username=...&password=..." automatically.
    const params = new URLSearchParams()
    params.append('username', email)   // OAuth2 convention uses "username" even for emails
    params.append('password', password)

    // POST the credentials to the backend login endpoint
    const response = await apiClient.post('/auth/login', params, {
      // Override the default JSON content type for this one request
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })

    // Destructure the JWT from the response body
    const { access_token } = response.data

    // Persist the token in localStorage so it survives page refreshes
    localStorage.setItem('ems_token', access_token)

    // Update the store so all components that read isAuthenticated re-render
    set({ token: access_token, isAuthenticated: true })

    // Return the full response data in case the caller needs it (e.g. to read user info)
    return response.data
  },

  // ── logout ───────────────────────────────────────────────────────────────
  // Called when the user clicks "Log out".
  // Clears the token everywhere so the app treats the user as logged out.
  logout: () => {
    // Remove the token from localStorage so it isn't restored on the next refresh
    localStorage.removeItem('ems_token')

    // Reset all auth-related state back to its initial "logged out" values
    set({ user: null, token: null, isAuthenticated: false })
  }
}))

// Export the hook so any component can call useAuthStore() to read or update auth state
export default useAuthStore

