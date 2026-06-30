import apiClient from '@/shared/utils/api-client'
import type { Employee, PaginatedResponse, EmploymentHistory } from '@/types/employee.types'

export interface EmployeeFilters {
  search?:         string
  departmentId?:   string
  jobPositionId?:  string
  employeeStatus?: string
  page?:           number
  pageSize?:       number
}

const employeesApi = {
  list: (filters: EmployeeFilters = {}) =>
    apiClient.get<PaginatedResponse<Employee>>('/employees/', { params: filters })
      .then(r => r.data),

  getById: (id: string) =>
    apiClient.get<Employee>(`/employees/${id}/`).then(r => r.data),

  create: (data: Partial<Employee>) =>
    apiClient.post<Employee>('/employees/', data).then(r => r.data),

  update: (id: string, data: Partial<Employee>) =>
    apiClient.patch<Employee>(`/employees/${id}/`, data).then(r => r.data),

  deactivate: (id: string) =>
    apiClient.delete(`/employees/${id}/`),

  reactivate: (id: string) =>
    apiClient.post(`/employees/${id}/reactivate/`),

  getHistory: (id: string) =>
    apiClient.get<EmploymentHistory[]>(`/employees/${id}/history/`)
      .then(r => r.data),
}

export default employeesApi