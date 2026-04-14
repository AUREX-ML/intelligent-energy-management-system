import { create } from 'zustand'
import apiClient from '../api/client'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('ems_token'),
  isAuthenticated: !!localStorage.getItem('ems_token'),

  login: async (email, password) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const response = await apiClient.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    const { access_token } = response.data
    localStorage.setItem('ems_token', access_token)
    set({ token: access_token, isAuthenticated: true })
    return response.data
  },

  logout: () => {
    localStorage.removeItem('ems_token')
    set({ user: null, token: null, isAuthenticated: false })
  }
}))

export default useAuthStore

