import { create } from 'zustand'
import { getAlerts, resolveAlert } from '../api/alerts'

const useAlertStore = create((set) => ({
  alerts: [],
  loading: false,
  error: null,

  fetchAlerts: async (params) => {
    set({ loading: true, error: null })
    try {
      const { data } = await getAlerts(params)
      set({ alerts: data, loading: false })
    } catch (err) {
      set({ error: err.message, loading: false })
    }
  },

  resolve: async (id) => {
    const { data } = await resolveAlert(id)
    set((state) => ({
      alerts: state.alerts.map((a) => (a.id === id ? data : a)),
    }))
  },
}))

export default useAlertStore
