import { useState, useEffect } from 'react'
import { getTelemetry } from '../api/telemetry'

export default function useTelemetry(deviceId) {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!deviceId) return
    setLoading(true)
    getTelemetry({ device_id: deviceId })
      .then(({ data }) => setData(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [deviceId])

  return { data, loading, error }
}
