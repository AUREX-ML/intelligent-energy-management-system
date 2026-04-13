import { create } from 'zustand'
import { login as apiLogin } from '../api/auth'

const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,

  login: async (credentials) => {
    const { data } = await apiLogin(credentials)
    localStorage.setItem('access_token', data.access_token)
    set({ token: data.access_token })
  },

  logout: () => {
    localStorage.removeItem('access_token')
    set({ user: null, token: null })
  },

  setUser: (user) => set({ user }),
}))

export default useAuthStore
