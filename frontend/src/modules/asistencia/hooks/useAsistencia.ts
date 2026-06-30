import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { asistenciaApi } from '../api/asistencia.api'

export const ATTENDANCE_KEY  = ['attendance-records']
export const LEAVES_KEY      = ['leave-requests']
export const BALANCES_KEY    = ['leave-balances']

export const useAttendanceRecords = (params?: string) =>
  useQuery({ queryKey: [...ATTENDANCE_KEY, params], queryFn: () => asistenciaApi.getRecords(params) })

export const useCheckIn = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ employeeId, notes }: { employeeId: string; notes?: string }) =>
      asistenciaApi.checkIn(employeeId, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ATTENDANCE_KEY }),
  })
}

export const useCheckOut = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ employeeId, notes }: { employeeId: string; notes?: string }) =>
      asistenciaApi.checkOut(employeeId, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ATTENDANCE_KEY }),
  })
}

export const useLeaveRequests = (params?: string) =>
  useQuery({ queryKey: [...LEAVES_KEY, params], queryFn: () => asistenciaApi.getLeaves(params) })

export const useCreateLeave = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: asistenciaApi.createLeave,
    onSuccess:  () => qc.invalidateQueries({ queryKey: LEAVES_KEY }),
  })
}

export const useReviewLeave = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, action, notes }: { id: string; action: 'approve'|'reject'; notes?: string }) =>
      asistenciaApi.reviewLeave(id, action, notes),
    onSuccess: () => qc.invalidateQueries({ queryKey: LEAVES_KEY }),
  })
}

export const useLeaveBalances = (employeeId?: string) =>
  useQuery({ queryKey: [...BALANCES_KEY, employeeId], queryFn: () => asistenciaApi.getBalances(employeeId) })
