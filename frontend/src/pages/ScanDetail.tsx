import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { CTScan } from '../types';
import { ArrowLeft, User, Clock, AlertTriangle, CheckCircle } from 'lucide-react';

const ScanDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<CTScan | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) loadScan(id);
  }, [id]);

  const loadScan = async (scanId: string) => {
    try {
      const data = await api.getScan(scanId);
      setScan(data);
    } catch (error) {
      console.error('Failed to load scan:', error);
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

  if (!scan) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">Scan not found</p>
        <Link to="/scans" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to scans
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        to="/scans"
        className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to scans
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">{scan.scan_number}</h1>
            <p className="text-slate-500">Patient ID: {scan.patient_id.slice(0, 8)}...</p>
          </div>
          <div className="flex items-center gap-3">
            <span
              className="inline-flex px-3 py-1 text-sm font-medium rounded-full"
              style={{
                backgroundColor: `${getUrgencyColor(scan.urgency_level)}20`,
                color: getUrgencyColor(scan.urgency_level),
              }}
            >
              {scan.urgency_level}
            </span>
            <span
              className="inline-flex px-3 py-1 text-sm font-medium rounded-full"
              style={{
                backgroundColor: `${getStatusColor(scan.status)}20`,
                color: getStatusColor(scan.status),
              }}
            >
              {scan.status}
            </span>
          </div>
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Clinical Information */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Clinical Information</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-500">CT Indication</p>
              <p className="text-slate-900 font-medium">{scan.ct_indication}</p>
            </div>
            <InfoRow label="Clinical History" value={scan.clinical_history || '-'} />
            <InfoRow label="Symptoms" value={scan.symptoms || '-'} />
            <InfoRow label="Neurological Findings" value={scan.neurological_findings || '-'} />
            {scan.gcs_score && (
              <InfoRow label="GCS Score" value={scan.gcs_score.toString()} icon={<AlertTriangle className="w-4 h-4" />} />
            )}
          </div>
        </div>

        {/* Scheduling & Status */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Scheduling & Status</h2>
          <div className="space-y-4">
            <InfoRow label="Contrast" value={scan.contrast} />
            <InfoRow label="Appropriateness Score" value={scan.appropriateness_score || '-'} />
            <InfoRow label="Ordered At" value={new Date(scan.ordered_at).toLocaleString()} icon={<Clock className="w-4 h-4" />} />
            <InfoRow label="Scheduled Time" value={scan.scheduled_time ? new Date(scan.scheduled_time).toLocaleString() : '-'} />
            <InfoRow label="Started Time" value={scan.started_time ? new Date(scan.started_time).toLocaleString() : '-'} />
            <InfoRow label="Completed Time" value={scan.completed_time ? new Date(scan.completed_time).toLocaleString() : '-'} />
          </div>
        </div>

        {/* Reports */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 md:col-span-2">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Reports</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-slate-500 mb-1">Preliminary Report</p>
              <div className="bg-slate-50 rounded-lg p-4 text-slate-900">
                {scan.preliminary_report || 'No preliminary report yet.'}
              </div>
            </div>
            <div>
              <p className="text-sm text-slate-500 mb-1">Final Report</p>
              <div className="bg-slate-50 rounded-lg p-4 text-slate-900">
                {scan.final_report || 'No final report yet.'}
              </div>
            </div>
            {scan.critical_findings && (
              <div className="flex items-center gap-2 bg-red-50 text-red-700 px-4 py-3 rounded-lg">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-medium">Critical Findings Detected</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow: React.FC<{ label: string; value: string; icon?: React.ReactNode }> = ({
  label,
  value,
  icon,
}) => (
  <div className="flex items-start gap-3">
    {icon && <span className="text-slate-400 mt-0.5">{icon}</span>}
    <div className="flex-1">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-slate-900">{value}</p>
    </div>
  </div>
);

export default ScanDetail;