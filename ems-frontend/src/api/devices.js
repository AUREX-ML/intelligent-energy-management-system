import api from './axiosClient'

export const getDevices = () => api.get('/devices')
export const getDevice = (id) => api.get(`/devices/${id}`)
export const createDevice = (data) => api.post('/devices', data)
export const updateDevice = (id, data) => api.patch(`/devices/${id}`, data)
export const deleteDevice = (id) => api.delete(`/devices/${id}`)
