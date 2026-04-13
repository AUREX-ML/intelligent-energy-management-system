import useDevices from '../hooks/useDevices'

export default function Devices() {
  const { devices, loading, error } = useDevices()

  if (loading) return <p className="p-6">Loading devices…</p>
  if (error) return <p className="p-6 text-red-500">{error}</p>

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Devices</h1>
      <ul className="space-y-2">
        {devices.map((device) => (
          <li key={device.id} className="border rounded p-3">
            <span className="font-medium">{device.name}</span>{' '}
            <span className="text-sm text-gray-500">({device.device_type})</span>
          </li>
        ))}
      </ul>
    </main>
  )
}
