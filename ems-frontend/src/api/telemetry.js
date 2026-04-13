import api from './axiosClient'

export const getTelemetry = (params) => api.get('/telemetry', { params })
export const ingestTelemetry = (data) => api.post('/telemetry', data)
