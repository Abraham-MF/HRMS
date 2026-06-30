export type PayrollStatus = 'CALCULADO' | 'APROBADO' | 'PAGADO' | 'CANCELADO'

export interface PayrollRecord {
  id:                  string
  employeeId:          string
  employeeName:        string
  periodId:            string
  periodLabel:         string
  baseSalary:          number
  extraHoursAmount:    number
  bonuses:             number
  commissions:         number
  otherIncome:         number
  grossSalary:         number
  isrDeduction:        number
  imssDeduction:       number
  infonavitDeduction:  number
  loansDeduction:      number
  otherDeductions:     number
  totalDeductions:     number
  netSalary:           number
  status:              PayrollStatus
  calculatedAt:        string
}

export interface PayrollPeriod {
  id:          string
  periodType:  'QUINCENAL' | 'MENSUAL' | 'SEMANAL'
  startDate:   string
  endDate:     string
  status:      'ABIERTO' | 'CERRADO' | 'PAGADO'
}