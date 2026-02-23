import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { Patient } from '../types';
import { ArrowLeft, User, Phone, Mail, MapPin, AlertCircle } from 'lucide-react';

const PatientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) loadPatient(id);
  }, [id]);

  const loadPatient = async (patientId: string) => {
    try {
      const data = await api.getPatient(patientId);
      setPatient(data);
    } catch (error) {
      console.error('Failed to load patient:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-500">Patient not found</p>
        <Link to="/patients" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to patients
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link
        to="/patients"
        className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to patients
      </Link>

      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">{patient.name}</h1>
              <p className="text-slate-500">MRN: {patient.mrn}</p>
            </div>
          </div>
          <span className="inline-flex px-3 py-1 text-sm font-medium rounded-full bg-slate-100 text-slate-700">
            {patient.status}
          </span>
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Personal Info */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Personal Information</h2>
          <div className="space-y-4">
            <InfoRow label="IC Number" value={patient.ic_number || '-'} />
            <InfoRow label="Date of Birth" value={new Date(patient.date_of_birth).toLocaleDateString()} />
            <InfoRow label="Gender" value={patient.gender} icon={<User className="w-4 h-4" />} />
            <InfoRow label="Phone" value={patient.phone || '-'} icon={<Phone className="w-4 h-4" />} />
            <InfoRow label="Email" value={patient.email || '-'} icon={<Mail className="w-4 h-4" />} />
            <InfoRow label="Address" value={patient.address || '-'} icon={<MapPin className="w-4 h-4" />} />
          </div>
        </div>

        {/* Clinical Info */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Clinical Information</h2>
          <div className="space-y-4">
            <InfoRow label="ED Visit ID" value={patient.ed_visit_id || '-'} />
            <InfoRow label="Ward" value={patient.ward || '-'} />
            <InfoRow label="Bed Number" value={patient.bed_number || '-'} />
            <InfoRow label="Chief Complaint" value={patient.chief_complaint || '-'} />
            <InfoRow label="Allergies" value={patient.allergies || 'None known'} icon={<AlertCircle className="w-4 h-4 text-red-500" />} />
            <InfoRow label="Anxiety Level" value={patient.anxiety_level} />
          </div>
        </div>

        {/* Consent Status */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Consent Status</h2>
          <div className="flex items-center gap-3">
            {patient.consent_given ? (
              <>
                <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                <span className="text-green-600 font-medium">Consent Given</span>
              </>
            ) : (
              <>
                <span className="w-3 h-3 bg-amber-500 rounded-full"></span>
                <span className="text-amber-600 font-medium">Pending Consent</span>
              </>
            )}
          </div>
        </div>

        {/* Notes */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Clinical Notes</h2>
          <p className="text-slate-600">{patient.clinical_notes || 'No clinical notes available.'}</p>
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

export default PatientDetail;