import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { CTScan, Patient } from '../types';
import { Scan, Search, Plus, Filter, X } from 'lucide-react';

const Scans: React.FC = () => {
  const [scans, setScans] = useState<CTScan[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    patient_id: '',
    ct_indication: '',
    clinical_history: '',
    symptoms: '',
    urgency_level: 'routine',
    contrast: 'without_contrast',
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [scansData, patientsData] = await Promise.all([
        api.getScans({ limit: 100 }),
        api.getPatients({ limit: 100 }),
      ]);
      setScans(scansData);
      setPatients(patientsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadScans = async () => {
    try {
      const data = await api.getScans({ limit: 100 });
      setScans(data);
    } catch (error) {
      console.error('Failed to load scans:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.createScan(formData);
      setShowModal(false);
      setFormData({
        patient_id: '',
        ct_indication: '',
        clinical_history: '',
        symptoms: '',
        urgency_level: 'routine',
        contrast: 'without_contrast',
      });
      loadScans();
    } catch (error) {
      console.error('Failed to create scan:', error);
      alert('Failed to create scan order');
    } finally {
      setSaving(false);
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

  const filteredScans = scans.filter((s) => {
    const matchesSearch =
      s.scan_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.ct_indication.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || s.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

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
          <h1 className="text-2xl font-bold text-slate-900">CT Scans</h1>
          <p className="text-slate-500">Manage CT Brain scan orders</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          New Scan Order
        </button>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by scan number or indication..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
          >
            <option value="">All Status</option>
            <option value="ordered">Ordered</option>
            <option value="validated">Validated</option>
            <option value="scheduled">Scheduled</option>
            <option value="in_prep">In Preparation</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="reported">Reported</option>
          </select>
        </div>
      </div>

      {/* Scans Table */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Scan #</th>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Indication</th>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Urgency</th>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Status</th>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Ordered</th>
              <th className="text-left py-3 px-6 text-sm font-medium text-slate-500">Scheduled</th>
            </tr>
          </thead>
          <tbody>
            {filteredScans.map((scan) => (
              <tr key={scan.id} className="border-b border-slate-100 hover:bg-slate-50">
                <td className="py-3 px-6 text-sm font-medium text-slate-900">
                  <Link to={`/scans/${scan.id}`} className="hover:text-primary-600">
                    {scan.scan_number}
                  </Link>
                </td>
                <td className="py-3 px-6 text-sm text-slate-600 max-w-xs truncate">
                  {scan.ct_indication}
                </td>
                <td className="py-3 px-6">
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
                <td className="py-3 px-6">
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
                <td className="py-3 px-6 text-sm text-slate-600">
                  {new Date(scan.ordered_at).toLocaleString()}
                </td>
                <td className="py-3 px-6 text-sm text-slate-600">
                  {scan.scheduled_time ? new Date(scan.scheduled_time).toLocaleString() : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* New Scan Order Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-slate-200">
              <h2 className="text-xl font-semibold text-slate-900">New CT Scan Order</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Patient *</label>
                <select
                  required
                  value={formData.patient_id}
                  onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="">Select a patient</option>
                  {patients.map((patient) => (
                    <option key={patient.id} value={patient.id}>
                      {patient.mrn} - {patient.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">CT Indication *</label>
                <textarea
                  required
                  value={formData.ct_indication}
                  onChange={(e) => setFormData({ ...formData, ct_indication: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  rows={3}
                  placeholder="Reason for CT scan (e.g., headache, suspected stroke, head trauma)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Clinical History</label>
                <textarea
                  value={formData.clinical_history}
                  onChange={(e) => setFormData({ ...formData, clinical_history: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  rows={2}
                  placeholder="Relevant clinical history"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Symptoms</label>
                <input
                  type="text"
                  value={formData.symptoms}
                  onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  placeholder="Current symptoms"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Urgency Level *</label>
                  <select
                    value={formData.urgency_level}
                    onChange={(e) => setFormData({ ...formData, urgency_level: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  >
                    <option value="routine">Routine (24 hours)</option>
                    <option value="urgent">Urgent (1 hour)</option>
                    <option value="immediate">Immediate</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Contrast *</label>
                  <select
                    value={formData.contrast}
                    onChange={(e) => setFormData({ ...formData, contrast: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                  >
                    <option value="without_contrast">Without Contrast</option>
                    <option value="with_contrast">With Contrast</option>
                    <option value="none">None</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {saving ? 'Creating...' : 'Create Scan Order'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Scans;