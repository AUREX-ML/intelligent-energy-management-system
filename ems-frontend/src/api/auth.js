import api from './axiosClient'

export const login = (credentials) => api.post('/auth/token', credentials)
export const getMe = () => api.get('/users/me')
