'use client'

import { useEffect, useState } from 'react'
import { Activity, ArrowUpRight, CheckCircle, XCircle, TrendingUp } from 'lucide-react'
import { apiClient } from '@/lib/api'
import StatsCard from '@/components/StatsCard'
import RecentActivity from '@/components/RecentActivity'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_requests: 0,
    active_routes: 0,
    uptime: 'Loading...',
    last_updated: new Date().toISOString()
  })
  const [health, setHealth] = useState<'healthy' | 'unhealthy' | 'loading'>('loading')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, healthData] = await Promise.all([
          apiClient.getStats(),
          apiClient.getHealth()
        ])
        setStats(statsData)
        setHealth(healthData.status === 'healthy' ? 'healthy' : 'unhealthy')
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        setHealth('unhealthy')
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your FastProxy instance</p>
      </div>

      {/* Status Banner */}
      <div className={`p-4 rounded-lg border ${
        health === 'healthy' 
          ? 'bg-green-50 border-green-200' 
          : health === 'unhealthy'
          ? 'bg-red-50 border-red-200'
          : 'bg-gray-50 border-gray-200'
      }`}>
        <div className="flex items-center gap-3">
          {health === 'healthy' ? (
            <CheckCircle className="h-6 w-6 text-green-600" />
          ) : health === 'unhealthy' ? (
            <XCircle className="h-6 w-6 text-red-600" />
          ) : (
            <Activity className="h-6 w-6 text-gray-600 animate-pulse" />
          )}
          <div>
            <h3 className="font-semibold text-gray-900">
              {health === 'healthy' 
                ? 'System Operational' 
                : health === 'unhealthy'
                ? 'System Issues Detected'
                : 'Checking System Status...'}
            </h3>
            <p className="text-sm text-gray-600">
              {health === 'healthy' 
                ? 'All systems are running normally' 
                : health === 'unhealthy'
                ? 'Please check your FastProxy configuration'
                : 'Loading system information...'}
            </p>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Requests"
          value={stats.total_requests.toLocaleString()}
          icon={<TrendingUp className="h-6 w-6" />}
          trend={{ value: 0, isPositive: true }}
          color="blue"
        />
        <StatsCard
          title="Active Routes"
          value={stats.active_routes.toString()}
          icon={<Activity className="h-6 w-6" />}
          color="green"
        />
        <StatsCard
          title="Uptime"
          value={stats.uptime}
          icon={<CheckCircle className="h-6 w-6" />}
          color="purple"
        />
        <StatsCard
          title="Response Time"
          value="< 50ms"
          icon={<ArrowUpRight className="h-6 w-6" />}
          trend={{ value: 15, isPositive: true }}
          color="orange"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity />
        
        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <a
              href="/routes"
              className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Manage Routes</h3>
              <p className="text-sm text-gray-600 mt-1">Add, edit, or remove proxy routes</p>
            </a>
            <a
              href="/api-keys"
              className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">API Keys</h3>
              <p className="text-sm text-gray-600 mt-1">Create and manage API keys</p>
            </a>
            <a
              href="/config"
              className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <h3 className="font-semibold text-gray-900">Configuration</h3>
              <p className="text-sm text-gray-600 mt-1">Update proxy settings</p>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

