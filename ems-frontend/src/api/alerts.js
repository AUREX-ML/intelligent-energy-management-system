import api from './axiosClient'

export const getAlerts = (params) => api.get('/alerts', { params })
export const getAlert = (id) => api.get(`/alerts/${id}`)
export const createAlert = (data) => api.post('/alerts', data)
export const resolveAlert = (id) => api.patch(`/alerts/${id}`, { is_resolved: true })
