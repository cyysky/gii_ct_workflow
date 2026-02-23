// User types
export type UserRole = 'ed_physician' | 'radiologist' | 'nurse' | 'technician' | 'admin' | 'transport';

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  department?: string;
  is_active: boolean;
}

// Patient types
export type Gender = 'male' | 'female' | 'other';
export type PatientStatus = 'registered' | 'waiting' | 'in_prep' | 'in_scan' | 'post_scan' | 'completed' | 'cancelled';
export type AnxietyLevel = 'none' | 'mild' | 'moderate' | 'severe';

export interface Patient {
  id: string;
  mrn: string;
  name: string;
  ic_number?: string;
  date_of_birth: string;
  gender: Gender;
  phone?: string;
  email?: string;
  address?: string;
  ed_visit_id?: string;
  ward?: string;
  bed_number?: string;
  chief_complaint?: string;
  clinical_notes?: string;
  allergies?: string;
  status: PatientStatus;
  anxiety_level: AnxietyLevel;
  consent_given: boolean;
  consent_timestamp?: string;
  registered_at: string;
  updated_at: string;
}

// CT Scan types
export type ScanStatus = 'ordered' | 'validated' | 'scheduled' | 'in_prep' | 'in_progress' | 'completed' | 'reported' | 'cancelled';
export type UrgencyLevel = 'immediate' | 'urgent' | 'routine';
export type AppropriatenessScore = 'very_high' | 'high' | 'moderate' | 'low' | 'very_low';
export type CTContrast = 'none' | 'with_contrast' | 'without_contrast';

export interface CTScan {
  id: string;
  scan_number: string;
  patient_id: string;
  ordering_physician_id?: string;
  radiology_technician_id?: string;
  radiologist_id?: string;
  scanner_id?: string;
  ct_indication: string;
  clinical_history?: string;
  symptoms?: string;
  onset_time?: string;
  gcs_score?: number;
  neurological_findings?: string;
  urgency_level: UrgencyLevel;
  appropriateness_score?: AppropriatenessScore;
  contrast: CTContrast;
  status: ScanStatus;
  scheduled_time?: string;
  started_time?: string;
  completed_time?: string;
  preliminary_report?: string;
  final_report?: string;
  critical_findings: boolean;
  ordered_at: string;
  created_at: string;
}

// Scanner types
export type ScannerStatus = 'available' | 'in_use' | 'maintenance' | 'out_of_service';
export type ScannerType = 'standard' | 'advanced' | 'dual_source';

export interface Scanner {
  id: string;
  scanner_code: string;
  name: string;
  location?: string;
  scanner_type: ScannerType;
  slice_count?: number;
  manufacturer?: string;
  model?: string;
  status: ScannerStatus;
  operational_hours_start: string;
  operational_hours_end: string;
  avg_scan_duration_minutes: number;
  daily_capacity: number;
  today_scans_completed: number;
  today_scans_scheduled: number;
  current_utilization: number;
  is_active: boolean;
  created_at: string;
}

// Dashboard types
export interface DashboardMetrics {
  total_patients_today: number;
  total_scans_today: number;
  scans_in_progress: number;
  scans_completed_today: number;
  scans_pending: number;
  avg_turnaround_time_minutes: number;
  scanner_utilization: number;
  critical_findings_today: number;
}

export interface ScanStatusCount {
  status: string;
  count: number;
}

export interface UrgencyDistribution {
  urgency_level: string;
  count: number;
}

export interface ScannerUtilization {
  scanner_id: string;
  scanner_code: string;
  status: string;
  today_scans: number;
  daily_capacity: number;
  utilization_percent: number;
}

// FAQ types
export interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
  keywords?: string;
  language: string;
  view_count: number;
  helpful_count: number;
  not_helpful_count: number;
  is_active: boolean;
  created_at: string;
}

// Auth types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}