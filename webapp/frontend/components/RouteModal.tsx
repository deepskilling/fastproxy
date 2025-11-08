'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'
import Button from './Button'

interface RouteModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (route: any) => void
  route?: any
}

export default function RouteModal({ isOpen, onClose, onSave, route }: RouteModalProps) {
  const [formData, setFormData] = useState({
    path: '',
    target: '',
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    auth_required: false,
    rate_limit: '',
  })

  useEffect(() => {
    if (route) {
      setFormData({
        path: route.path || '',
        target: route.target || '',
        methods: route.methods || ['GET', 'POST', 'PUT', 'DELETE'],
        auth_required: route.auth_required || false,
        rate_limit: route.rate_limit?.toString() || '',
      })
    } else {
      setFormData({
        path: '',
        target: '',
        methods: ['GET', 'POST', 'PUT', 'DELETE'],
        auth_required: false,
        rate_limit: '',
      })
    }
  }, [route, isOpen])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const routeData = {
      ...formData,
      rate_limit: formData.rate_limit ? parseInt(formData.rate_limit) : undefined,
    }
    onSave(routeData)
  }

  const toggleMethod = (method: string) => {
    setFormData((prev) => ({
      ...prev,
      methods: prev.methods.includes(method)
        ? prev.methods.filter((m) => m !== method)
        : [...prev.methods, method],
    }))
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {route ? 'Edit Route' : 'Add New Route'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Path Pattern *
            </label>
            <input
              type="text"
              required
              value={formData.path}
              onChange={(e) => setFormData({ ...formData, path: e.target.value })}
              placeholder="/api/users"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">The path pattern to match (e.g., /api/*, /users/:id)</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target URL *
            </label>
            <input
              type="url"
              required
              value={formData.target}
              onChange={(e) => setFormData({ ...formData, target: e.target.value })}
              placeholder="https://backend.example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">The backend URL to proxy requests to</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              HTTP Methods
            </label>
            <div className="flex gap-2 flex-wrap">
              {['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].map((method) => (
                <button
                  key={method}
                  type="button"
                  onClick={() => toggleMethod(method)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    formData.methods.includes(method)
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {method}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Rate Limit (requests per minute)
            </label>
            <input
              type="number"
              value={formData.rate_limit}
              onChange={(e) => setFormData({ ...formData, rate_limit: e.target.value })}
              placeholder="Leave empty for unlimited"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="auth_required"
              checked={formData.auth_required}
              onChange={(e) => setFormData({ ...formData, auth_required: e.target.checked })}
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <label htmlFor="auth_required" className="text-sm font-medium text-gray-700">
              Require Authentication
            </label>
          </div>

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <Button type="submit" className="flex-1">
              {route ? 'Update Route' : 'Create Route'}
            </Button>
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}

