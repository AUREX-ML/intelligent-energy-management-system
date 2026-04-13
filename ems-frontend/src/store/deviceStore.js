import { create } from 'zustand'
import { getDevices, createDevice, updateDevice, deleteDevice } from '../api/devices'

const useDeviceStore = create((set) => ({
  devices: [],
  loading: false,
  error: null,

  fetchDevices: async () => {
    set({ loading: true, error: null })
    try {
      const { data } = await getDevices()
      set({ devices: data, loading: false })
    } catch (err) {
      set({ error: err.message, loading: false })
    }
  },

  addDevice: async (payload) => {
    const { data } = await createDevice(payload)
    set((state) => ({ devices: [...state.devices, data] }))
  },

  editDevice: async (id, payload) => {
    const { data } = await updateDevice(id, payload)
    set((state) => ({
      devices: state.devices.map((d) => (d.id === id ? data : d)),
    }))
  },

  removeDevice: async (id) => {
    await deleteDevice(id)
    set((state) => ({ devices: state.devices.filter((d) => d.id !== id) }))
  },
}))

export default useDeviceStore
