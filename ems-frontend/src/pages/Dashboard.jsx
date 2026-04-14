import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import apiClient from '../api/client'

export default function DashboardPage({ buildingId }) {
  const [kpis, setKpis] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [trend, setTrend] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpiRes, alertRes] = await Promise.all([
          apiClient.get(`/buildings/${buildingId}/dashboard`),
          apiClient.get(`/alerts/?building_id=${buildingId}&status=open`)
        ])
        setKpis(kpiRes.data.kpis)
        setAlerts(alertRes.data)
        setTrend(kpiRes.data.trend)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
    // FR-2: Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [buildingId])

  if (loading) return <div className="p-6">Loading dashboard...</div>

  return (
    <div className="p-6 space-y-6">
      {/* KPI Cards — FR-7 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="Total Energy (kWh)" value={kpis?.total_energy_kwh} />
        <KpiCard label="Peak Demand (kW)" value={kpis?.peak_demand_kw} />
        <KpiCard label="Avg Power Factor" value={kpis?.avg_power_factor} />
        <KpiCard label="Est. Cost (KES)" value={kpis?.estimated_cost_kes} />
      </div>

      {/* Trend chart — FR-18 */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Power Trend (kW)</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Active alerts — FR-26, FR-22 */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Alerts</h2>
        {alerts.length === 0 ? (
          <p className="text-green-600">No active alerts</p>
        ) : (
          <ul className="space-y-2">
            {alerts.map(alert => (
              <li key={alert.id} className={`p-3 rounded-lg border ${
                alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                alert.severity === 'high' ? 'border-orange-400 bg-orange-50' :
                'border-yellow-300 bg-yellow-50'
              }`}>
                <strong>{alert.severity.toUpperCase()}</strong> — {alert.metric_name} |{' '}
                {alert.triggered_value} | {new Date(alert.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

function KpiCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 text-center">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-blue-700">{value ?? '—'}</p>
    </div>
  )
}