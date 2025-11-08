'use client'

import { useEffect, useState } from 'react'
import { Activity } from 'lucide-react'
import { format } from 'date-fns'

interface ActivityItem {
  id: string
  type: 'route_added' | 'route_deleted' | 'config_updated' | 'key_created'
  message: string
  timestamp: Date
}

export default function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([
    {
      id: '1',
      type: 'route_added',
      message: 'New route added: /api/users',
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: '2',
      type: 'config_updated',
      message: 'Configuration updated',
      timestamp: new Date(Date.now() - 900000),
    },
    {
      id: '3',
      type: 'key_created',
      message: 'API key created: Production Key',
      timestamp: new Date(Date.now() - 1800000),
    },
  ])

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'route_added':
        return 'bg-green-100 text-green-800'
      case 'route_deleted':
        return 'bg-red-100 text-red-800'
      case 'config_updated':
        return 'bg-blue-100 text-blue-800'
      case 'key_created':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="h-5 w-5 text-gray-700" />
        <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
      </div>

      <div className="space-y-3">
        {activities.length === 0 ? (
          <p className="text-gray-500 text-sm">No recent activity</p>
        ) : (
          activities.map((activity) => (
            <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50">
              <div className={`p-2 rounded-full ${getActivityColor(activity.type)}`}>
                <Activity className="h-4 w-4" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900">{activity.message}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {format(activity.timestamp, 'MMM d, yyyy HH:mm')}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

