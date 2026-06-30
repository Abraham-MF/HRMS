import { useAuthStore } from '@/modules/auth/store/authStore'

export const usePermissions = () => {
  const { user } = useAuthStore()
  const role = user?.role

  return {
    isAdmin:       role === 'ADMIN',
    isHR:          role === 'HR' || role === 'ADMIN',
    isSupervisor:  role === 'SUPERVISOR' || role === 'HR' || role === 'ADMIN',
    isEmployee:    !!role,
    canEdit:       role === 'ADMIN' || role === 'HR',
    canDelete:     role === 'ADMIN',
    canApproveLeave: role === 'ADMIN' || role === 'HR' || role === 'SUPERVISOR',
    canViewPayroll:  role === 'ADMIN' || role === 'HR',
    canApprovePayroll: role === 'ADMIN',
    canExportReports:  role === 'ADMIN' || role === 'HR',
  }
}