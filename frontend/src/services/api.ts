import axios, { AxiosInstance, AxiosError } from 'axios';
import { useAuthStore } from '../hooks/useAuth';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          const { logout } = useAuthStore.getState();
          logout();
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(username: string, password: string) {
    const response = await this.api.post('/auth/login', { username, password });
    return response.data;
  }

  async register(data: {
    email: string;
    username: string;
    password: string;
    full_name: string;
    role: string;
  }) {
    const response = await this.api.post('/auth/register', data);
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.api.get('/auth/me');
    return response.data;
  }

  // Patients
  async getPatients(params?: { status?: string; skip?: number; limit?: number }) {
    const response = await this.api.get('/patients/', { params });
    return response.data;
  }

  async getPatient(id: string) {
    const response = await this.api.get(`/patients/${id}`);
    return response.data;
  }

  async createPatient(data: any) {
    const response = await this.api.post('/patients/', data);
    return response.data;
  }

  async updatePatient(id: string, data: any) {
    const response = await this.api.put(`/patients/${id}`, data);
    return response.data;
  }

  // CT Scans
  async getScans(params?: { status?: string; patient_id?: string; skip?: number; limit?: number }) {
    const response = await this.api.get('/scans/', { params });
    return response.data;
  }

  async getScan(id: string) {
    const response = await this.api.get(`/scans/${id}`);
    return response.data;
  }

  async createScan(data: any) {
    const response = await this.api.post('/scans/', data);
    return response.data;
  }

  async updateScan(id: string, data: any) {
    const response = await this.api.put(`/scans/${id}`, data);
    return response.data;
  }

  async updateScanStatus(id: string, status: string) {
    const response = await this.api.patch(`/scans/${id}/status?new_status=${status}`);
    return response.data;
  }

  // Resources
  async getScanners(params?: { status?: string; is_active?: boolean }) {
    const response = await this.api.get('/resources/scanners', { params });
    return response.data;
  }

  async getAvailableScanners() {
    const response = await this.api.get('/resources/scanners/available');
    return response.data;
  }

  async createScanner(data: any) {
    const response = await this.api.post('/resources/scanners', data);
    return response.data;
  }

  async updateScanner(id: string, data: any) {
    const response = await this.api.put(`/resources/scanners/${id}`, data);
    return response.data;
  }

  async updateScannerStatus(id: string, status: string) {
    const response = await this.api.patch(`/resources/scanners/${id}/status?new_status=${status}`);
    return response.data;
  }

  // Dashboard
  async getDashboardMetrics() {
    const response = await this.api.get('/dashboard/metrics');
    return response.data;
  }

  async getScanStatusDistribution() {
    const response = await this.api.get('/dashboard/scan-status');
    return response.data;
  }

  async getUrgencyDistribution() {
    const response = await this.api.get('/dashboard/urgency-distribution');
    return response.data;
  }

  async getScannerUtilization() {
    const response = await this.api.get('/dashboard/scanner-utilization');
    return response.data;
  }

  async getRecentScans(limit: number = 10) {
    const response = await this.api.get('/dashboard/recent-scans', { params: { limit } });
    return response.data;
  }

  // FAQ
  async getFAQs(params?: { category?: string; is_active?: boolean; skip?: number; limit?: number }) {
    const response = await this.api.get('/faq/', { params });
    return response.data;
  }

  async getFAQCategories() {
    const response = await this.api.get('/faq/categories');
    return response.data;
  }

  // Users
  async getUsers(params?: { role?: string; is_active?: boolean; skip?: number; limit?: number }) {
    const response = await this.api.get('/users/', { params });
    return response.data;
  }
}

export const api = new ApiService();
export default api;