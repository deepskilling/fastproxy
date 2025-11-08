'use client'

import { useEffect, useState } from 'react'
import { Save, RefreshCw } from 'lucide-react'
import { apiClient } from '@/lib/api'
import Button from '@/components/Button'

export default function ConfigPage() {
  const [config, setConfig] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)

  const fetchConfig = async () => {
    try {
      setLoading(true)
      const data = await apiClient.getConfig()
      setConfig(JSON.stringify(data.config, null, 2))
    } catch (error) {
      console.error('Error fetching config:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchConfig()
  }, [])

  const handleSave = async () => {
    try {
      setSaving(true)
      const configObj = JSON.parse(config)
      await apiClient.updateConfig(configObj)
      setLastSaved(new Date())
      alert('Configuration saved successfully!')
    } catch (error: any) {
      console.error('Error saving config:', error)
      if (error instanceof SyntaxError) {
        alert('Invalid JSON format. Please check your configuration.')
      } else {
        alert('Failed to save configuration')
      }
    } finally {
      setSaving(false)
    }
  }

  const handleReload = async () => {
    if (confirm('Reload configuration? Any unsaved changes will be lost.')) {
      await fetchConfig()
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Configuration</h1>
          <p className="text-gray-600 mt-2">Edit FastProxy configuration (YAML format as JSON)</p>
        </div>
        <div className="flex gap-3">
          <Button
            variant="secondary"
            onClick={handleReload}
            icon={<RefreshCw className="h-4 w-4" />}
            disabled={loading}
          >
            Reload
          </Button>
          <Button
            onClick={handleSave}
            icon={<Save className="h-4 w-4" />}
            disabled={saving || loading}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      {lastSaved && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <p className="text-sm text-green-800">
            Last saved: {lastSaved.toLocaleTimeString()}
          </p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Configuration (JSON)
          </label>
          <p className="text-sm text-gray-500 mb-4">
            ⚠️ Warning: Invalid configuration may cause FastProxy to stop working. Always validate before saving.
          </p>
        </div>

        {loading ? (
          <div className="bg-gray-50 rounded-lg p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading configuration...</p>
          </div>
        ) : (
          <textarea
            value={config}
            onChange={(e) => setConfig(e.target.value)}
            className="w-full h-[600px] font-mono text-sm p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            spellCheck={false}
          />
        )}

        <div className="mt-4 flex items-start gap-2 text-sm text-gray-600">
          <span>💡</span>
          <div>
            <p className="font-medium">Tips:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Use proper JSON syntax with double quotes for strings</li>
              <li>Test changes in a development environment first</li>
              <li>Keep a backup of your working configuration</li>
              <li>Restart FastProxy after making changes for them to take effect</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

