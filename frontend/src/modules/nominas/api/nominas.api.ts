import apiClient from '@/shared/utils/api-client'
import type { PayrollPeriod, PayrollRecord } from '@/types/nominas.types'

const BASE = '/payroll'

export const nominasApi = {
  getPeriods: () =>
    apiClient.get<{ results: PayrollPeriod[] }>(`${BASE}/periods/`).then(r => r.data.results),
  createPeriod: (data: Omit<PayrollPeriod, 'id'>) =>
    apiClient.post<PayrollPeriod>(`${BASE}/periods/`, data).then(r => r.data),
  calculatePeriod: (id: string) =>
    apiClient.post(`${BASE}/periods/${id}/calculate/`).then(r => r.data),
  approvePeriod: (id: string) =>
    apiClient.post(`${BASE}/periods/${id}/approve/`).then(r => r.data),
  payPeriod: (id: string) =>
    apiClient.post(`${BASE}/periods/${id}/pay/`).then(r => r.data),
  getRecords: (periodId?: string) => {
    const params = periodId ? `?period=${periodId}` : ''
    return apiClient.get<{ results: PayrollRecord[] }>(`${BASE}/records/${params}`).then(r => r.data.results)
  },
  recalculate: (id: string, adjustments: Record<string, number>) =>
    apiClient.post<PayrollRecord>(`${BASE}/records/${id}/recalculate/`, adjustments).then(r => r.data),
}
