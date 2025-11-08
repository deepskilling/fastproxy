'use client'

import { useEffect, useState } from 'react'
import { Plus, Trash2, Edit, ExternalLink } from 'lucide-react'
import { apiClient } from '@/lib/api'
import Button from '@/components/Button'
import RouteModal from '@/components/RouteModal'

interface Route {
  path: string
  target: string
  methods?: string[]
  auth_required?: boolean
  rate_limit?: number
}

export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingRoute, setEditingRoute] = useState<Route | null>(null)

  const fetchRoutes = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getRoutes()
      setRoutes(data.routes || [])
    } catch (error) {
      console.error('Error fetching routes:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRoutes()
  }, [])

  const handleAddRoute = () => {
    setEditingRoute(null)
    setIsModalOpen(true)
  }

  const handleEditRoute = (route: Route) => {
    setEditingRoute(route)
    setIsModalOpen(true)
  }

  const handleDeleteRoute = async (path: string) => {
    if (!confirm('Are you sure you want to delete this route?')) return

    try {
      await apiClient.deleteRoute(path)
      await fetchRoutes()
    } catch (error) {
      console.error('Error deleting route:', error)
      alert('Failed to delete route')
    }
  }

  const handleSaveRoute = async (route: Route) => {
    try {
      if (editingRoute) {
        // For editing, we need to delete old and create new
        await apiClient.deleteRoute(editingRoute.path)
      }
      await apiClient.addRoute(route)
      await fetchRoutes()
      setIsModalOpen(false)
    } catch (error) {
      console.error('Error saving route:', error)
      alert('Failed to save route')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Proxy Routes</h1>
          <p className="text-gray-600 mt-2">Manage your proxy route configurations</p>
        </div>
        <Button onClick={handleAddRoute} icon={<Plus className="h-4 w-4" />}>
          Add Route
        </Button>
      </div>

      {loading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading routes...</p>
        </div>
      ) : routes.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">No routes configured yet.</p>
          <Button onClick={handleAddRoute} className="mt-4">
            Add Your First Route
          </Button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Path
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Target
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Methods
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Auth
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Rate Limit
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {routes.map((route, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <code className="text-sm font-mono text-gray-900">{route.path}</code>
                      <a
                        href={route.target}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900">{route.target}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-1">
                      {(route.methods || ['GET', 'POST', 'PUT', 'DELETE']).map((method) => (
                        <span
                          key={method}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {method}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        route.auth_required
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {route.auth_required ? 'Required' : 'None'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {route.rate_limit ? `${route.rate_limit}/min` : 'Unlimited'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEditRoute(route)}
                      className="text-primary-600 hover:text-primary-900 mr-4"
                    >
                      <Edit className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteRoute(route.path.replace(/^\//, ''))}
                      className="text-red-600 hover:text-red-900"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <RouteModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRoute}
        route={editingRoute}
      />
    </div>
  )
}

