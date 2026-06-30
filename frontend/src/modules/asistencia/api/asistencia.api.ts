import apiClient from '@/shared/utils/api-client'
import type { AttendanceRecord, LeaveRequest, LeaveBalance } from '@/types/asistencia.types'

const BASE = '/attendance'

export const asistenciaApi = {
  getRecords: (params?: string) =>
    apiClient.get<{ results: AttendanceRecord[] }>(`${BASE}/records/${params ?? ''}`).then(r => r.data.results),
  checkIn: (employeeId: string, notes?: string) =>
    apiClient.post(`${BASE}/records/check-in/`, { employee_id: employeeId, notes }).then(r => r.data),
  checkOut: (employeeId: string, notes?: string) =>
    apiClient.post(`${BASE}/records/check-out/`, { employee_id: employeeId, notes }).then(r => r.data),

  getLeaves: (params?: string) =>
    apiClient.get<{ results: LeaveRequest[] }>(`${BASE}/leaves/${params ?? ''}`).then(r => r.data.results),
  createLeave: (data: Partial<LeaveRequest>) =>
    apiClient.post<LeaveRequest>(`${BASE}/leaves/`, data).then(r => r.data),
  reviewLeave: (id: string, action: 'approve'|'reject', notes?: string) =>
    apiClient.post(`${BASE}/leaves/${id}/review/`, { action, review_notes: notes }).then(r => r.data),

  getBalances: (employeeId?: string) => {
    const params = employeeId ? `?employee=${employeeId}` : ''
    return apiClient.get<{ results: LeaveBalance[] }>(`${BASE}/balances/${params}`).then(r => r.data.results)
  },
}
