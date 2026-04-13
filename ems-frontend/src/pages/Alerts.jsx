import { useEffect, useState } from 'react'
import useAlertStore from '../store/alertStore'
import { formatDate } from '../utils/helpers'

export default function Alerts() {
  const { alerts, loading, error, fetchAlerts, resolve } = useAlertStore()

  useEffect(() => {
    fetchAlerts()
  }, [fetchAlerts])

  if (loading) return <p className="p-6">Loading alerts…</p>
  if (error) return <p className="p-6 text-red-500">{error}</p>

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Alerts</h1>
      <ul className="space-y-2">
        {alerts.map((alert) => (
          <li key={alert.id} className="border rounded p-3 flex justify-between items-center">
            <div>
              <span className={`font-semibold capitalize ${alert.severity === 'critical' ? 'text-red-600' : alert.severity === 'warning' ? 'text-yellow-600' : 'text-blue-600'}`}>
                [{alert.severity}]
              </span>{' '}
              {alert.message}
              <div className="text-xs text-gray-400 mt-1">{formatDate(alert.triggered_at)}</div>
            </div>
            {!alert.is_resolved && (
              <button
                onClick={() => resolve(alert.id)}
                className="ml-4 px-3 py-1 bg-green-500 text-white rounded text-sm hover:bg-green-600"
              >
                Resolve
              </button>
            )}
          </li>
        ))}
      </ul>
    </main>
  )
}
