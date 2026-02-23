import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Scanner } from '../types';
import { HardDrive, Plus, Search } from 'lucide-react';

const Resources: React.FC = () => {
  const [scanners, setScanners] = useState<Scanner[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScanners();
  }, []);

  const loadScanners = async () => {
    try {
      const data = await api.getScanners({ is_active: true });
      setScanners(data);
    } catch (error) {
      console.error('Failed to load scanners:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      available: '#10b981',
      in_use: '#0ea5e9',
      maintenance: '#f59e0b',
      out_of_service: '#ef4444',
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
          <h1 className="text-2xl font-bold text-slate-900">Resources</h1>
          <p className="text-slate-500">CT Scanner management</p>
        </div>
        <button className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700">
          <Plus className="w-4 h-4" />
          Add Scanner
        </button>
      </div>

      {/* Scanner Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {scanners.map((scanner) => (
          <div
            key={scanner.id}
            className="bg-white rounded-xl shadow-sm border border-slate-200 p-6"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-slate-100 rounded-lg">
                  <HardDrive className="w-6 h-6 text-slate-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">{scanner.scanner_code}</h3>
                  <p className="text-sm text-slate-500">{scanner.name}</p>
                </div>
              </div>
              <span
                className="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                style={{
                  backgroundColor: `${getStatusColor(scanner.status)}20`,
                  color: getStatusColor(scanner.status),
                }}
              >
                {scanner.status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Location</span>
                <span className="text-slate-900">{scanner.location || '-'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Type</span>
                <span className="text-slate-900 capitalize">{scanner.scanner_type}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Slice Count</span>
                <span className="text-slate-900">{scanner.slice_count || '-'}</span>
              </div>

              <div className="pt-3 border-t border-slate-100">
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-slate-500">Today's Utilization</span>
                  <span className="text-slate-900 font-medium">
                    {scanner.current_utilization}%
                  </span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      scanner.current_utilization > 80
                        ? 'bg-red-500'
                        : scanner.current_utilization > 50
                        ? 'bg-amber-500'
                        : 'bg-green-500'
                    }`}
                    style={{ width: `${Math.min(scanner.current_utilization, 100)}%` }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>{scanner.today_scans_completed} completed</span>
                  <span>{scanner.daily_capacity} capacity</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Operating Hours</span>
                  <span className="text-slate-900">
                    {scanner.operational_hours_start} - {scanner.operational_hours_end}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {scanners.length === 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center">
          <HardDrive className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No scanners found</h3>
          <p className="text-slate-500">Add CT scanners to start managing resources.</p>
        </div>
      )}
    </div>
  );
};

export default Resources;