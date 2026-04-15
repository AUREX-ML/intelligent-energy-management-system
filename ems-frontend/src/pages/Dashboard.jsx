// useEffect runs side-effects (like data fetching) after the component renders.
// useState lets us store pieces of data that, when changed, cause the UI to re-render.
import { useEffect, useState } from 'react'

// Recharts components used to draw the energy trend line chart
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

// The pre-configured axios instance that automatically attaches the JWT to every request
import apiClient from '../api/client'

// DashboardPage is the main page component.
// It receives `buildingId` as a prop so it knows which building's data to load.
export default function DashboardPage({ buildingId }) {
  // kpis holds the key performance indicator numbers returned by the backend (null until loaded)
  const [kpis, setKpis] = useState(null)

  // alerts holds the list of currently open alerts for this building (empty array by default)
  const [alerts, setAlerts] = useState([])

  // trend holds the time-series data points used to draw the line chart
  const [trend, setTrend] = useState([])

  // loading is true while we're waiting for the first API response; used to show a loading message
  const [loading, setLoading] = useState(true)

  // useEffect runs fetchData when the component first mounts and again whenever buildingId changes.
  // The dependency array [buildingId] at the bottom tells React when to re-run this effect.
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Promise.all fires both requests at the same time and waits for both to finish.
        // This is faster than awaiting them one at a time.
        const [kpiRes, alertRes] = await Promise.all([
          // GET dashboard KPIs and trend data for this building
          apiClient.get(`/buildings/${buildingId}/dashboard`),
          // GET only the open (unresolved) alerts for this building
          apiClient.get(`/alerts/?building_id=${buildingId}&status=open`)
        ])

        // Store each piece of data in its own state variable so the UI re-renders with fresh values
        setKpis(kpiRes.data.kpis)
        setAlerts(alertRes.data)
        setTrend(kpiRes.data.trend)
      } finally {
        // Always hide the loading indicator once the requests finish (whether they succeeded or not)
        setLoading(false)
      }
    }

    fetchData() // Run immediately on mount

    // FR-2: Refresh every 10 seconds so the dashboard stays up to date without a full page reload.
    // setInterval calls fetchData repeatedly at the given interval (10 000 ms = 10 s).
    const interval = setInterval(fetchData, 10000)

    // Cleanup function: React calls this when the component is unmounted or buildingId changes.
    // Clearing the interval prevents fetchData from running after the component is gone.
    return () => clearInterval(interval)
  }, [buildingId])

  // Show a simple loading message while the first data fetch is in progress
  if (loading) return <div className="p-6">Loading dashboard...</div>

  return (
    <div className="p-6 space-y-6">
      {/* KPI Cards — FR-7: display the four main energy metrics in a responsive grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Each KpiCard receives a label and the matching value from the kpis object.
            The ?. (optional chaining) safely returns undefined if kpis is null. */}
        <KpiCard label="Total Energy (kWh)" value={kpis?.total_energy_kwh} />
        <KpiCard label="Peak Demand (kW)" value={kpis?.peak_demand_kw} />
        <KpiCard label="Avg Power Factor" value={kpis?.avg_power_factor} />
        <KpiCard label="Est. Cost (KES)" value={kpis?.estimated_cost_kes} />
      </div>

      {/* Trend chart — FR-18: visualise active power over time as a line chart */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Power Trend (kW)</h2>

        {/* ResponsiveContainer makes the chart fill the full width of its parent element */}
        <ResponsiveContainer width="100%" height={300}>
          {/* LineChart takes the `trend` array as its data source */}
          <LineChart data={trend}>
            {/* Grid lines in the background to make values easier to read */}
            <CartesianGrid strokeDasharray="3 3" />

            {/* X-axis uses the "time" field from each data point */}
            <XAxis dataKey="time" />

            {/* Y-axis is auto-scaled by Recharts based on the data range */}
            <YAxis />

            {/* Tooltip shows the exact value when the user hovers over the chart */}
            <Tooltip />

            {/* The actual line: draws the "value" field, blue colour, no dots on each point */}
            <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Active alerts — FR-26, FR-22: list open alerts colour-coded by severity */}
      <div className="bg-white rounded-xl shadow p-4">
        <h2 className="text-lg font-semibold mb-4">Active Alerts</h2>

        {/* Conditional rendering: show a friendly message when there are no alerts */}
        {alerts.length === 0 ? (
          <p className="text-green-600">No active alerts</p>
        ) : (
          <ul className="space-y-2">
            {/* .map() loops over the alerts array and renders one <li> per alert */}
            {alerts.map(alert => (
              // key={alert.id} is required by React to efficiently track list items
              <li key={alert.id} className={`p-3 rounded-lg border ${
                // Apply different border/background colours depending on severity level
                alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                alert.severity === 'high' ? 'border-orange-400 bg-orange-50' :
                'border-yellow-300 bg-yellow-50'
              }`}>
                {/* Show severity in uppercase, then the metric name and triggered value */}
                <strong>{alert.severity.toUpperCase()}</strong> — {alert.metric_name} |{' '}
                {/* Format the ISO timestamp into a human-readable local date/time string */}
                {alert.triggered_value} | {new Date(alert.created_at).toLocaleString()}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}

// ── KpiCard ──────────────────────────────────────────────────────────────────
// A small reusable card component that displays a single KPI metric.
// `label` is the display name; `value` is the number to show.
function KpiCard({ label, value }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 text-center">
      {/* Metric name in small grey text */}
      <p className="text-sm text-gray-500">{label}</p>

      {/* Metric value in large bold blue text.
          The ?? '—' (nullish coalescing) shows a dash if the value is null or undefined. */}
      <p className="text-2xl font-bold text-blue-700">{value ?? '—'}</p>
    </div>
  )
}