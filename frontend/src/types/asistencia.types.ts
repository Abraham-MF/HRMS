export type LeaveStatus   = 'PENDIENTE' | 'APROBADA' | 'RECHAZADA' | 'CANCELADA'
export type LeaveType     = 'VACACIONES' | 'PERSONAL' | 'MEDICO' | 'DUELO' | 'OTRO'
export type LicenseType   = 'INCAPACIDAD' | 'MATERNIDAD' | 'PATERNIDAD' | 'PERMISO_ESPECIAL' | 'PERMISO_SIN_GOCE'

export interface AttendanceRecord {
  id:           string
  employee:     string
  employeeName: string
  workDate:     string
  checkIn:      string | null
  checkOut:     string | null
  hoursWorked:  number | null
  extraHours:   number
  lateMinutes:  number
  isAbsence:    boolean
  notes:        string
}

export interface LeaveRequest {
  id:           string
  employee:     string
  employeeName: string
  leaveType:    LeaveType
  startDate:    string
  endDate:      string
  totalDays:    number
  reason:       string
  status:       LeaveStatus
  reviewNotes:  string
  requestedAt:  string
  reviewedAt:   string | null
  durationDays: number
}

export interface LeaveBalance {
  id:            string
  employee:      string
  employeeName:  string
  year:          number
  entitledDays:  number
  usedDays:      number
  pendingDays:   number
  remainingDays: number
}
