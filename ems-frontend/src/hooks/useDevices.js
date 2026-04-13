import { useEffect } from 'react'
import useDeviceStore from '../store/deviceStore'

export default function useDevices() {
  const { devices, loading, error, fetchDevices } = useDeviceStore()

  useEffect(() => {
    fetchDevices()
  }, [fetchDevices])

  return { devices, loading, error, refetch: fetchDevices }
}
