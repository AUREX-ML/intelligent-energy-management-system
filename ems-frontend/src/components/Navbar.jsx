import { Link, NavLink } from 'react-router-dom'

export default function Navbar() {
  const linkClass = ({ isActive }) =>
    `px-3 py-2 rounded text-sm font-medium ${isActive ? 'bg-blue-600 text-white' : 'text-gray-700 hover:bg-gray-100'}`

  return (
    <nav className="border-b bg-white px-6 py-3 flex items-center gap-4">
      <Link to="/" className="font-bold text-blue-600 text-lg mr-4">EMS</Link>
      <NavLink to="/" className={linkClass} end>Dashboard</NavLink>
      <NavLink to="/devices" className={linkClass}>Devices</NavLink>
      <NavLink to="/telemetry" className={linkClass}>Telemetry</NavLink>
      <NavLink to="/alerts" className={linkClass}>Alerts</NavLink>
    </nav>
  )
}
