export type EmployeeStatus   = 'ACTIVO' | 'BAJA' | 'SUSPENDIDO' | 'VACACIONES'
export type ContractType     = 'INDEFINIDO' | 'DETERMINADO' | 'HONORARIOS'
export type Gender           = 'MASCULINO' | 'FEMENINO' | 'NO_BINARIO'
export type ChangeType       =
  | 'SALARY_CHANGE' | 'DEPARTMENT_CHANGE' | 'POSITION_CHANGE'
  | 'PROMOTION'     | 'TRANSFER'          | 'REHIRE' | 'STATUS_CHANGE'

export interface Employee {
  id:              string
  employeeNumber:  string
  firstName:       string
  lastName:        string
  fullName:        string
  curp:            string
  rfc:             string
  birthDate:       string
  age:             number
  gender:          Gender
  maritalStatus:   string
  nationality:     string
  address:         string
  city:            string
  state:           string
  postalCode:      string
  phone:           string
  email:           string
  departmentId:    string
  departmentName:  string
  jobPositionId:   string
  positionTitle:   string
  supervisorId:    string | null
  supervisorName:  string | null
  hireDate:        string
  contractType:    ContractType
  baseSalary:      number
  employeeStatus:  EmployeeStatus
  isActive:        boolean
  createdAt:       string
}

export interface EmploymentHistory {
  id:            string
  changeType:    ChangeType
  previousValue: string
  newValue:      string
  notes:         string
  changedAt:     string
}

export interface Department {
  id:          string
  name:        string
  code:        string
  description: string
  parentId:    string | null
  isActive:    boolean
}

export interface JobPosition {
  id:             string
  title:          string
  code:           string
  departmentId:   string
  departmentName: string
  minSalary:      number | null
  maxSalary:      number | null
  isActive:       boolean
}

export interface PaginatedResponse<T> {
  count:       number
  next:        string | null
  previous:    string | null
  totalPages:  number
  currentPage: number
  results:     T[]
}