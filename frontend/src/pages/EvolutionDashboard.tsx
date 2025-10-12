import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Shield,
  Zap,
  BarChart3,
  Clock
} from 'lucide-react';

interface EvolutionMetrics {
  total_events: number;
  pending_improvements: number;
  applied_improvements: number;
  success_rate: number;
  average_confidence: number;
  safe_mode_active: boolean;
  last_evolution: string;
}

interface AnomalyData {
  metric_name: string;
  latest_value: number;
  mean: number;
  z_score: number;
  severity: string;
  timestamp: string;
}

interface PerformanceData {
  nba_success_rate: number;
  reminder_success_rate: number;
  avg_response_time: number;
}

const EvolutionDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<EvolutionMetrics | null>(null);
  const [anomalies, setAnomalies] = useState<AnomalyData[]>([]);
  const [performance, setPerformance] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvolutionData();
    const interval = setInterval(fetchEvolutionData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchEvolutionData = async () => {
    try {
      // In production, these would be real API calls
      // For now, using mock data
      setMetrics({
        total_events: 42,
        pending_improvements: 3,
        applied_improvements: 39,
        success_rate: 0.93,
        average_confidence: 0.85,
        safe_mode_active: false,
        last_evolution: new Date().toISOString()
      });

      setAnomalies([]);

      setPerformance({
        nba_success_rate: 0.87,
        reminder_success_rate: 0.92,
        avg_response_time: 245
      });

      setLoading(false);
    } catch (error) {
      console.error('Error fetching evolution data:', error);
      setLoading(false);
    }
  };

  const toggleSafeMode = async () => {
    try {
      // In production, this would call the API to toggle safe mode
      console.log('Toggling safe mode...');
      if (metrics) {
        setMetrics({
          ...metrics,
          safe_mode_active: !metrics.safe_mode_active
        });
      }
    } catch (error) {
      console.error('Error toggling safe mode:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">Loading evolution dashboard...</div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Evolution Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Monitor and control the self-evolution framework
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSafeMode}
            className={`px-6 py-2 rounded-lg font-semibold flex items-center space-x-2 ${
              metrics?.safe_mode_active
                ? 'bg-red-500 hover:bg-red-600 text-white'
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            <Shield className="w-5 h-5" />
            <span>
              {metrics?.safe_mode_active ? 'Safe Mode: ON' : 'Safe Mode: OFF'}
            </span>
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Evolution Events</p>
              <p className="text-3xl font-bold mt-2">{metrics?.total_events}</p>
            </div>
            <Activity className="w-12 h-12 text-blue-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-3xl font-bold mt-2">
                {((metrics?.success_rate || 0) * 100).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-12 h-12 text-green-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Pending Improvements</p>
              <p className="text-3xl font-bold mt-2">
                {metrics?.pending_improvements}
              </p>
            </div>
            <Clock className="w-12 h-12 text-yellow-500" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Avg Confidence</p>
              <p className="text-3xl font-bold mt-2">
                {((metrics?.average_confidence || 0) * 100).toFixed(0)}%
              </p>
            </div>
            <Zap className="w-12 h-12 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Anomaly Detection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <AlertTriangle className="w-6 h-6 mr-2 text-orange-500" />
          Anomaly Detection
        </h2>
        {anomalies.length === 0 ? (
          <div className="flex items-center text-green-600">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>No anomalies detected</span>
          </div>
        ) : (
          <div className="space-y-3">
            {anomalies.map((anomaly, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-l-4 ${
                  anomaly.severity === 'critical'
                    ? 'border-red-500 bg-red-50'
                    : anomaly.severity === 'high'
                    ? 'border-orange-500 bg-orange-50'
                    : 'border-yellow-500 bg-yellow-50'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold">{anomaly.metric_name}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      Value: {anomaly.latest_value.toFixed(2)} (Mean:{' '}
                      {anomaly.mean.toFixed(2)}, Z-Score:{' '}
                      {anomaly.z_score.toFixed(2)})
                    </p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      anomaly.severity === 'critical'
                        ? 'bg-red-200 text-red-800'
                        : anomaly.severity === 'high'
                        ? 'bg-orange-200 text-orange-800'
                        : 'bg-yellow-200 text-yellow-800'
                    }`}
                  >
                    {anomaly.severity.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4 flex items-center">
          <BarChart3 className="w-6 h-6 mr-2 text-blue-500" />
          System Performance
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <p className="text-gray-600 text-sm mb-2">NBA Success Rate</p>
            <div className="flex items-center">
              <div className="flex-1 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-green-500 h-4 rounded-full"
                  style={{
                    width: `${(performance?.nba_success_rate || 0) * 100}%`
                  }}
                ></div>
              </div>
              <span className="ml-3 font-semibold">
                {((performance?.nba_success_rate || 0) * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div>
            <p className="text-gray-600 text-sm mb-2">Reminder Success Rate</p>
            <div className="flex items-center">
              <div className="flex-1 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-500 h-4 rounded-full"
                  style={{
                    width: `${(performance?.reminder_success_rate || 0) * 100}%`
                  }}
                ></div>
              </div>
              <span className="ml-3 font-semibold">
                {((performance?.reminder_success_rate || 0) * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          <div>
            <p className="text-gray-600 text-sm mb-2">Avg Response Time</p>
            <div className="flex items-center">
              <div className="flex-1 bg-gray-200 rounded-full h-4">
                <div
                  className="bg-purple-500 h-4 rounded-full"
                  style={{
                    width: `${Math.min(
                      ((performance?.avg_response_time || 0) / 1000) * 100,
                      100
                    )}%`
                  }}
                ></div>
              </div>
              <span className="ml-3 font-semibold">
                {performance?.avg_response_time}ms
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Evolution Events */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Recent Evolution Events</h2>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <div>
                <p className="font-semibold">NBA Rule Optimization</p>
                <p className="text-sm text-gray-600">
                  Improved confidence threshold for customer segment A
                </p>
              </div>
            </div>
            <span className="text-sm text-gray-500">2 hours ago</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <div>
                <p className="font-semibold">Reminder Timing Optimization</p>
                <p className="text-sm text-gray-600">
                  Adjusted preferred hours based on response patterns
                </p>
              </div>
            </div>
            <span className="text-sm text-gray-500">5 hours ago</span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Clock className="w-5 h-5 text-yellow-500" />
              <div>
                <p className="font-semibold">Code Quality Improvement</p>
                <p className="text-sm text-gray-600">
                  Pending review: Refactored NBA decision engine
                </p>
              </div>
            </div>
            <span className="text-sm text-gray-500">1 day ago</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EvolutionDashboard;

