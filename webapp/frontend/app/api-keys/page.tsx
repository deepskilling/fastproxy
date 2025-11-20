'use client'

import { useEffect, useState } from 'react'
import { Plus, Trash2, Copy, Key } from 'lucide-react'
import { format } from 'date-fns'
import { apiClient } from '@/lib/api'
import Button from '@/components/Button'
import ApiKeyModal from '@/components/ApiKeyModal'

interface ApiKey {
  id: string
  name: string
  key?: string
  created_at: string
  expires_at?: string
  permissions: string[]
}

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)

  const fetchApiKeys = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getApiKeys()
      setApiKeys(data.keys || [])
    } catch (error) {
      console.error('Error fetching API keys:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchApiKeys()
  }, [])

  const handleCreateKey = async (data: { name: string; permissions: string[]; expires_in_days?: number }) => {
    try {
      const result = await apiClient.createApiKey(data)
      setNewKey(result.key)
      await fetchApiKeys()
    } catch (error) {
      console.error('Error creating API key:', error)
      alert('Failed to create API key')
    }
  }

  const handleDeleteKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return

    try {
      await apiClient.revokeApiKey(keyId)
      await fetchApiKeys()
    } catch (error) {
      console.error('Error revoking API key:', error)
      alert('Failed to revoke API key')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
          <p className="text-gray-600 mt-2">Manage authentication keys for FastProxy</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} icon={<Plus className="h-4 w-4" />}>
          Create API Key
        </Button>
      </div>

      {newKey && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Key className="h-6 w-6 text-green-600 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-green-900">API Key Created Successfully!</h3>
              <p className="text-sm text-green-700 mt-1">
                Make sure to copy your API key now. You won&apos;t be able to see it again!
              </p>
              <div className="mt-3 flex items-center gap-2">
                <code className="flex-1 bg-white border border-green-300 rounded px-3 py-2 text-sm font-mono">
                  {newKey}
                </code>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => copyToClipboard(newKey)}
                  icon={<Copy className="h-4 w-4" />}
                >
                  Copy
                </Button>
              </div>
            </div>
            <button
              onClick={() => setNewKey(null)}
              className="text-green-600 hover:text-green-800"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="text-gray-600 mt-4">Loading API keys...</p>
        </div>
      ) : apiKeys.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <Key className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No API keys created yet.</p>
          <Button onClick={() => setIsModalOpen(true)} className="mt-4">
            Create Your First API Key
          </Button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Key
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Permissions
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Expires
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {apiKeys.map((apiKey) => (
                <tr key={apiKey.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm font-medium text-gray-900">{apiKey.name}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <code className="text-sm font-mono text-gray-600">
                      {apiKey.key ? apiKey.key.substring(0, 20) + '...' : 'fp_••••••••'}
                    </code>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex gap-1">
                      {apiKey.permissions.map((perm) => (
                        <span
                          key={perm}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {perm}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {format(new Date(apiKey.created_at), 'MMM d, yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {apiKey.expires_at ? format(new Date(apiKey.expires_at), 'MMM d, yyyy') : 'Never'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDeleteKey(apiKey.id)}
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

      <ApiKeyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreateKey}
      />
    </div>
  )
}

