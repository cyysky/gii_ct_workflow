import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuthStore } from '../hooks/useAuth';
import api from '../services/api';
import {
  DashboardMetrics,
  ScanStatusCount,
  ScannerUtilization,
  CTScan,
} from '../types';
import {
  Users,
  Scan,
  Clock,
  AlertTriangle,
  CheckCircle,
  HardDrive,
  TrendingUp,
  Activity,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const Dashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [statusDist, setStatusDist] = useState<ScanStatusCount[]>([]);
  const [scannerUtil, setScannerUtil] = useState<ScannerUtilization[]>([]);
  const [recentScans, setRecentScans] = useState<CTScan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [metricsData, statusData, utilData, scansData] = await Promise.all([
        api.getDashboardMetrics(),
        api.getScanStatusDistribution(),
        api.getScannerUtilization(),
        api.getRecentScans(5),
      ]);
      setMetrics(metricsData);
      setStatusDist(statusData);
      setScannerUtil(utilData);
      setRecentScans(scansData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUrgencyColor = (urgency: string) => {
    const colors: Record<string, string> = {
      immediate: '#ef4444',
      urgent: '#f59e0b',
      routine: '#10b981',
    };
    return colors[urgency] || '#6b7280';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      ordered: '#6b7280',
      validated: '#3b82f6',
      scheduled: '#8b5cf6',
      in_prep: '#f59e0b',
      in_progress: '#0ea5e9',
      completed: '#10b981',
      reported: '#22c55e',
      cancelled: '#ef4444',
    };
    return colors[status] || '#6b7280';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-500">Welcome back, {user?.full_name}</p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Activity className="w-4 h-4" />
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Patients Today"
          value={metrics?.total_patients_today || 0}
          icon={Users}
          color="bg-blue-500"
        />
        <MetricCard
          title="Scans Today"
          value={metrics?.total_scans_today || 0}
          icon={Scan}
          color="bg-purple-500"
        />
        <MetricCard
          title="In Progress"
          value={metrics?.scans_in_progress || 0}
          icon={Activity}
          color="bg-amber-500"
        />
        <MetricCard
          title="Avg TAT"
          value={`${metrics?.avg_turnaround_time_minutes || 0}m`}
          icon={Clock}
          color="bg-green-500"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scan Status Distribution */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Scan Status Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusDist}
                  dataKey="count"
                  nameKey="status"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ status, count }) => `${status}: ${count}`}
                >
                  {statusDist.map((entry, index) => (
                    <Cell key={index} fill={getStatusColor(entry.status)} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Scanner Utilization */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Scanner Utilization</h3>
          <div className="space-y-4">
            {scannerUtil.map((scanner) => (
              <div key={scanner.scanner_id} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{scanner.scanner_code}</span>
                  <span className="text-slate-500">
                    {scanner.today_scans}/{scanner.daily_capacity} ({scanner.utilization_percent}%)
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      scanner.utilization_percent > 80
                        ? 'bg-red-500'
                        : scanner.utilization_percent > 50
                        ? 'bg-amber-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(scanner.utilization_percent, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Pending Scans</h3>
            <span className="bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-sm font-medium">
              {metrics?.scans_pending || 0}
            </span>
          </div>
          <Link
            to="/scans"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            View all pending scans →
          </Link>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Critical Findings</h3>
            <span className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-medium">
              {metrics?.critical_findings_today || 0}
            </span>
          </div>
          <p className="text-slate-500 text-sm">Today's critical findings requiring attention</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-900">Completed Today</h3>
            <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium">
              {metrics?.scans_completed_today || 0}
            </span>
          </div>
          <p className="text-slate-500 text-sm">Total scans completed today</p>
        </div>
      </div>

      {/* Recent Scans */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Scans</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Scan #</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Patient ID</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Urgency</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Status</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-slate-500">Ordered At</th>
              </tr>
            </thead>
            <tbody>
              {recentScans.map((scan) => (
                <tr key={scan.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 px-4 text-sm font-medium text-slate-900">
                    <Link to={`/scans/${scan.id}`} className="hover:text-primary-600">
                      {scan.scan_number}
                    </Link>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-600">{scan.patient_id.slice(0, 8)}...</td>
                  <td className="py-3 px-4">
                    <span
                      className="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                      style={{
                        backgroundColor: `${getUrgencyColor(scan.urgency_level)}20`,
                        color: getUrgencyColor(scan.urgency_level),
                      }}
                    >
                      {scan.urgency_level}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                      style={{
                        backgroundColor: `${getStatusColor(scan.status)}20`,
                        color: getStatusColor(scan.status),
                      }}
                    >
                      {scan.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-slate-600">
                    {new Date(scan.ordered_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.FC<{ className?: string }>;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, icon: Icon, color }) => (
  <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-slate-500">{title}</p>
        <p className="text-2xl font-bold text-slate-900 mt-1">{value}</p>
      </div>
      <div className={`p-3 rounded-lg ${color}`}>
        <Icon className="w-6 h-6 text-white" />
      </div>
    </div>
  </div>
);

export default Dashboard;