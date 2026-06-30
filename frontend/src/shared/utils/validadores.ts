import { z } from 'zod'

const CURP_REGEX = /^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$/
const RFC_REGEX  = /^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$/
const CP_REGEX   = /^\d{5}$/

export const employeeSchema = z.object({
  employeeNumber: z.string().min(1, 'Número de empleado requerido'),
  firstName:      z.string().min(2, 'Mínimo 2 caracteres').max(100),
  lastName:       z.string().min(2, 'Mínimo 2 caracteres').max(100),
  curp:           z.string().regex(CURP_REGEX, 'CURP inválida (formato: XXXX######XXXXXX#)'),
  rfc:            z.string().regex(RFC_REGEX,  'RFC inválido'),
  birthDate:      z.string().refine(d => {
    const age = new Date().getFullYear() - new Date(d).getFullYear()
    return age >= 18 && age <= 80
  }, 'El empleado debe tener entre 18 y 80 años'),
  gender:         z.enum(['MASCULINO', 'FEMENINO', 'NO_BINARIO']),
  email:          z.string().email('Correo inválido'),
  phone:          z.string().optional(),
  address:        z.string().optional(),
  city:           z.string().optional(),
  state:          z.string().optional(),
  postalCode:     z.string().regex(CP_REGEX, 'Código postal inválido').optional().or(z.literal('')),
  departmentId:   z.string().uuid('Selecciona un departamento'),
  jobPositionId:  z.string().uuid('Selecciona un cargo'),
  supervisorId:   z.string().uuid().optional().nullable(),
  hireDate:       z.string().min(1, 'Fecha de contratación requerida'),
  contractType:   z.enum(['INDEFINIDO', 'DETERMINADO', 'HONORARIOS']),
  baseSalary:     z.coerce.number().positive('El salario debe ser mayor a cero'),
  maritalStatus:  z.string().optional(),
  nationality:    z.string().optional(),
})

export type EmployeeFormData = z.infer<typeof employeeSchema>