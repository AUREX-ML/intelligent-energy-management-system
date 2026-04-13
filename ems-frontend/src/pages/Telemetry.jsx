import useTelemetry from '../hooks/useTelemetry'
import { formatDate } from '../utils/helpers'

export default function Telemetry() {
  // TODO: replace with a device selector component
  const deviceId = null
  const { data, loading, error } = useTelemetry(deviceId)

  if (!deviceId) return <p className="p-6 text-gray-400">Select a device to view telemetry.</p>
  if (loading) return <p className="p-6">Loading telemetry…</p>
  if (error) return <p className="p-6 text-red-500">{error}</p>

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Telemetry</h1>
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-3 py-2 text-left">Metric</th>
            <th className="border px-3 py-2 text-left">Value</th>
            <th className="border px-3 py-2 text-left">Unit</th>
            <th className="border px-3 py-2 text-left">Recorded At</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id}>
              <td className="border px-3 py-2">{row.metric}</td>
              <td className="border px-3 py-2">{row.value}</td>
              <td className="border px-3 py-2">{row.unit ?? '—'}</td>
              <td className="border px-3 py-2">{formatDate(row.recorded_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  )
}
