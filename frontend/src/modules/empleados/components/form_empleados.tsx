import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { employeeSchema } from '@/shared/utils/validators'
import { Button } from '@/shared/components/ui/Button'
import { useQuery } from '@tanstack/react-query'
import apiClient from '@/shared/utils/api-client'
import type { Department, JobPosition } from '@/types/employee.types'

// Tipo derivado localmente para evitar conflicto de inferencia con zod .default()
type EmployeeFormData = z.infer<typeof employeeSchema>

interface EmployeeFormProps {
  defaultValues?: Partial<EmployeeFormData>
  onSubmit:       (data: EmployeeFormData) => Promise<void>
  isLoading?:     boolean
}

const Field = ({ label, error, children, required = false }: {
  label: string; error?: string; children: React.ReactNode; required?: boolean
}) => (
  <div className="space-y-1">
    <label className="block text-sm font-medium text-gray-700">
      {label}{required && <span className="text-red-500 ml-1">*</span>}
    </label>
    {children}
    {error && <p className="text-xs text-red-600">{error}</p>}
  </div>
)

const inputClass = `w-full px-3 py-2 text-sm border rounded-lg bg-white
  focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent
  border-gray-200 placeholder-gray-400`

export default function EmployeeForm({ defaultValues, onSubmit, isLoading }: EmployeeFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<EmployeeFormData>({
    resolver:      zodResolver(employeeSchema) as any,
    defaultValues: defaultValues ?? { nationality: 'Mexicana', contractType: 'INDEFINIDO' },
  })

  const { data: departments } = useQuery({
    queryKey: ['departments'],
    queryFn:  () => apiClient.get<{ results: Department[] }>('/employees/departments/')
      .then(r => r.data.results),
  })

  const { data: positions } = useQuery({
    queryKey: ['job-positions'],
    queryFn:  () => apiClient.get<{ results: JobPosition[] }>('/employees/positions/')
      .then(r => r.data.results),
  })

  return (
    <form onSubmit={handleSubmit(onSubmit as any)} className="space-y-8">
      {/* Información personal */}
      <section>
        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider
          pb-2 border-b border-gray-100 mb-4">
          Información personal
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Field label="Nombre(s)" error={errors.firstName?.message} required>
            <input {...register('firstName')} placeholder="Juan" className={inputClass}/>
          </Field>
          <Field label="Apellidos" error={errors.lastName?.message} required>
            <input {...register('lastName')} placeholder="García López" className={inputClass}/>
          </Field>
          <Field label="CURP" error={errors.curp?.message} required>
            <input {...register('curp')}
              placeholder="GARL901225HMCRCN01"
              className={`${inputClass} uppercase`}
              maxLength={18}/>
          </Field>
          <Field label="RFC" error={errors.rfc?.message} required>
            <input {...register('rfc')}
              placeholder="GARL901225AB1"
              className={`${inputClass} uppercase`}
              maxLength={13}/>
          </Field>
          <Field label="Fecha de nacimiento" error={errors.birthDate?.message} required>
            <input type="date" {...register('birthDate')} className={inputClass}/>
          </Field>
          <Field label="Género" error={errors.gender?.message} required>
            <select {...register('gender')} className={inputClass}>
              <option value="">Seleccionar...</option>
              <option value="MASCULINO">Masculino</option>
              <option value="FEMENINO">Femenino</option>
              <option value="NO_BINARIO">No binario</option>
            </select>
          </Field>
          <Field label="Estado civil" error={errors.maritalStatus?.message}>
            <select {...register('maritalStatus')} className={inputClass}>
              <option value="">Seleccionar...</option>
              <option value="SOLTERO">Soltero/a</option>
              <option value="CASADO">Casado/a</option>
              <option value="DIVORCIADO">Divorciado/a</option>
              <option value="VIUDO">Viudo/a</option>
              <option value="UNION_LIBRE">Unión libre</option>
            </select>
          </Field>
          <Field label="Correo electrónico" error={errors.email?.message} required>
            <input type="email" {...register('email')}
              placeholder="juan@empresa.com" className={inputClass}/>
          </Field>
          <Field label="Teléfono" error={errors.phone?.message}>
            <input {...register('phone')} placeholder="+52 55 1234 5678" className={inputClass}/>
          </Field>
          <Field label="Dirección" error={errors.address?.message}>
            <input {...register('address')} placeholder="Calle y número" className={inputClass}/>
          </Field>
          <Field label="Ciudad" error={errors.city?.message}>
            <input {...register('city')} placeholder="Ciudad de México" className={inputClass}/>
          </Field>
          <Field label="Estado" error={errors.state?.message}>
            <input {...register('state')} placeholder="Ciudad de México" className={inputClass}/>
          </Field>
          <Field label="Código postal" error={errors.postalCode?.message}>
            <input {...register('postalCode')} placeholder="06600" maxLength={5}
              className={inputClass}/>
          </Field>
        </div>
      </section>

      {/* Información laboral */}
      <section>
        <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider
          pb-2 border-b border-gray-100 mb-4">
          Información laboral
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Field label="Número de empleado" error={errors.employeeNumber?.message} required>
            <input {...register('employeeNumber')} placeholder="EMP-0001" className={inputClass}/>
          </Field>
          <Field label="Departamento" error={errors.departmentId?.message} required>
            <select {...register('departmentId')} className={inputClass}>
              <option value="">Seleccionar...</option>
              {departments?.map(d => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </Field>
          <Field label="Cargo" error={errors.jobPositionId?.message} required>
            <select {...register('jobPositionId')} className={inputClass}>
              <option value="">Seleccionar...</option>
              {positions?.map(p => (
                <option key={p.id} value={p.id}>{p.title}</option>
              ))}
            </select>
          </Field>
          <Field label="Fecha de contratación" error={errors.hireDate?.message} required>
            <input type="date" {...register('hireDate')} className={inputClass}/>
          </Field>
          <Field label="Tipo de contrato" error={errors.contractType?.message} required>
            <select {...register('contractType')} className={inputClass}>
              <option value="INDEFINIDO">Contrato indefinido</option>
              <option value="DETERMINADO">Tiempo determinado</option>
              <option value="HONORARIOS">Honorarios</option>
            </select>
          </Field>
          <Field label="Salario base (MXN)" error={errors.baseSalary?.message} required>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">
                $
              </span>
              <input type="number" step="0.01" min="0"
                {...register('baseSalary')}
                placeholder="0.00"
                className={`${inputClass} pl-7`}/>
            </div>
          </Field>
        </div>
      </section>

      {/* Acciones */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
        <Button type="button" variant="secondary"
          onClick={() => history.back()}>
          Cancelar
        </Button>
        <Button type="submit" loading={isLoading}>
          Guardar empleado
        </Button>
      </div>
    </form>
  )
}
