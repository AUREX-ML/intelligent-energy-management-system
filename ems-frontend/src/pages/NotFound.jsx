import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-2">404</h1>
      <p className="text-gray-500 mb-4">Page not found.</p>
      <Link to="/" className="text-blue-600 hover:underline">Back to Dashboard</Link>
    </div>
  )
}
