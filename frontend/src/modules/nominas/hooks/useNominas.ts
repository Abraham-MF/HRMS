import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { nominasApi } from '../api/nominas.api'

export const PERIODS_KEY = ['payroll-periods']

export const usePayrollPeriods = () =>
  useQuery({ queryKey: PERIODS_KEY, queryFn: nominasApi.getPeriods })

export const usePayrollRecords = (periodId?: string) =>
  useQuery({
    queryKey: ['payroll-records', periodId],
    queryFn:  () => nominasApi.getRecords(periodId),
    enabled:  !!periodId,
  })

export const useCalculatePeriod = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: nominasApi.calculatePeriod,
    onSuccess:  () => qc.invalidateQueries({ queryKey: PERIODS_KEY }),
  })
}

export const useApprovePeriod = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: nominasApi.approvePeriod,
    onSuccess:  () => qc.invalidateQueries({ queryKey: PERIODS_KEY }),
  })
}

export const usePayPeriod = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: nominasApi.payPeriod,
    onSuccess:  () => qc.invalidateQueries({ queryKey: PERIODS_KEY }),
  })
}
