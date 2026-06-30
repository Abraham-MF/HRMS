import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Search, Filter } from 'lucide-react'
import { useEmployees, useDeactivateEmployee } from '../hooks/useEmployees'
import { usePermissions } from '@/shared/hooks/usePermissions'
import { Button }    from '@/shared/components/ui/Button'
import { Badge, employeeStatusBadge } from '@/shared/components/ui/Badge'
import { Modal }     from '@/shared/components/ui/Modal'
import { formatDate, formatCurrency } from '@/shared/utils/formatters'
import useDebounce   from '@/shared/hooks/useDebounce'
import type { Employee } from '@/types/employee.types'

export default function EmployeeListPage() {
  const navigate     = useNavigate()
  const { canEdit, canDelete } = usePermissions()
  const [search, setSearch]   = useState('')
  const [page, setPage]       = useState(1)
  const [filters, setFilters] = useState<Record<string,string>>({})
  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null)

  const debouncedSearch = useDebounce(search, 400)
  const { data, isLoading, isFetching } = useEmployees({
    search: debouncedSearch, page, ...filters
  })
  const deactivate = useDeactivateEmployee()

  const handleDelete = async () => {
    if (!deleteTarget) return
    await deactivate.mutateAsync(deleteTarget.id)
    setDeleteTarget(null)
  }

  return (
    <div className="space-y-6">
      {/* Encabezado */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Empleados</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            {data?.count ?? 0} empleados registrados
          </p>
        </div>
        {canEdit && (
          <Button icon={<Plus size={16}/>}
            onClick={() => navigate('/employees/new')}>
            Nuevo empleado
          </Button>
        )}
      </div>

      {/* Barra de búsqueda y filtros */}
      <div className="flex gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2
            text-gray-400"/>
          <input
            value={search}
            onChange={e => { setSearch(e.target.value); setPage(1) }}
            placeholder="Buscar por nombre o número..."
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200
              rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-400
              bg-white"
          />
        </div>
        <select
          onChange={e => setFilters(f => ({ ...f, employeeStatus: e.target.value }))}
          className="px-3 py-2 text-sm border border-gray-200 rounded-lg
            bg-white focus:outline-none focus:ring-2 focus:ring-primary-400">
          <option value="">Todos los estatus</option>
          <option value="ACTIVO">Activo</option>
          <option value="VACACIONES">En vacaciones</option>
          <option value="SUSPENDIDO">Suspendido</option>
          <option value="BAJA">Baja</option>
        </select>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                {['Empleado','Departamento','Cargo','Salario','Ingreso','Estatus',''].map(h => (
                  <th key={h} className="px-4 py-3 text-left text-xs font-medium
                    text-gray-500 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading
                ? Array.from({length: 8}).map((_, i) => (
                    <tr key={i}><td colSpan={7} className="px-4 py-3">
                      <div className="h-4 bg-gray-100 rounded animate-pulse"/>
                    </td></tr>
                  ))
                : data?.results.map(emp => (
                    <tr key={emp.id}
                      className="hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => navigate(`/employees/${emp.id}`)}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 bg-primary-100 rounded-full flex
                            items-center justify-center text-primary-800
                            font-medium text-xs flex-shrink-0">
                            {emp.firstName[0]}{emp.lastName[0]}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900">{emp.fullName}</p>
                            <p className="text-xs text-gray-500">{emp.employeeNumber}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{emp.departmentName}</td>
                      <td className="px-4 py-3 text-gray-700">{emp.positionTitle}</td>
                      <td className="px-4 py-3 text-gray-700 font-mono">
                        {formatCurrency(emp.baseSalary)}
                      </td>
                      <td className="px-4 py-3 text-gray-500">
                        {formatDate(emp.hireDate)}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={employeeStatusBadge(emp.employeeStatus)}>
                          {emp.employeeStatus}
                        </Badge>
                      </td>
                      <td className="px-4 py-3" onClick={e => e.stopPropagation()}>
                        {canDelete && (
                          <button
                            onClick={() => setDeleteTarget(emp)}
                            className="text-gray-400 hover:text-red-600
                              transition-colors text-xs">
                            Dar de baja
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
              }
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        {data && data.totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3
            border-t border-gray-100">
            <p className="text-xs text-gray-500">
              Página {data.currentPage} de {data.totalPages}
            </p>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm"
                disabled={!data.previous}
                onClick={() => setPage(p => p - 1)}>
                Anterior
              </Button>
              <Button variant="secondary" size="sm"
                disabled={!data.next}
                onClick={() => setPage(p => p + 1)}>
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Modal confirmación baja */}
      <Modal
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="Confirmar baja de empleado"
        size="sm"
        footer={<>
          <Button variant="secondary" onClick={() => setDeleteTarget(null)}>
            Cancelar
          </Button>
          <Button variant="danger" loading={deactivate.isPending}
            onClick={handleDelete}>
            Confirmar baja
          </Button>
        </>}
      >
        <p className="text-sm text-gray-600">
          ¿Confirmas la baja lógica de{' '}
          <span className="font-medium text-gray-900">
            {deleteTarget?.fullName}
          </span>?
          El registro se conservará en el sistema con estatus BAJA.
        </p>
      </Modal>
    </div>
  )
}