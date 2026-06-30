import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import employeesApi, { type EmployeeFilters } from '../api'
import toast from 'react-hot-toast'

export const EMPLOYEES_KEY = 'employees'

export const useEmployees = (filters: EmployeeFilters = {}) =>
  useQuery({
    queryKey: [EMPLOYEES_KEY, 'list', filters],
    queryFn:  () => employeesApi.list(filters),
    staleTime: 30_000,//30 segundos de cache
    placeholderData: (prev) => prev,//mantener datos anteriores mientras recarga
  })

export const useEmployee = (id: string) =>
  useQuery({
    queryKey: [EMPLOYEES_KEY, 'detail', id],
    queryFn:  () => employeesApi.getById(id),
    enabled:  !!id,
    staleTime: 60_000,
  })

export const useEmployeeHistory = (id: string) =>
  useQuery({
    queryKey: [EMPLOYEES_KEY, 'history', id],
    queryFn:  () => employeesApi.getHistory(id),
    enabled:  !!id,
  })

export const useCreateEmployee = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: employeesApi.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [EMPLOYEES_KEY] })
      toast.success('Empleado registrado correctamente')
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.error?.message || 'Error al registrar empleado')
    },
  })
}

export const useUpdateEmployee = (id: string) => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Parameters<typeof employeesApi.update>[1]) =>
      employeesApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [EMPLOYEES_KEY] })
      toast.success('Empleado actualizado correctamente')
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.error?.message || 'Error al actualizar')
    },
  })
}

export const useDeactivateEmployee = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: employeesApi.deactivate,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [EMPLOYEES_KEY] })
      toast.success('Empleado dado de baja correctamente')
    },
    onError: () => toast.error('Error al dar de baja al empleado'),
  })
}