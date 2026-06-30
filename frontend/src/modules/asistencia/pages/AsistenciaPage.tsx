import { useState } from 'react'
import { useAttendanceRecords, useLeaveRequests, useReviewLeave, useCreateLeave } from '../hooks/useAsistencia'
import { Badge } from '@/shared/components/ui/Badge'
import { Button } from '@/shared/components/ui/Button'
import type { LeaveType } from '@/types/asistencia.types'

type Tab = 'registros' | 'permisos' | 'solicitar'

interface AsistenciaPageProps {
  initialTab?: Tab
}

function statusBadge(s: string) {
  const map: Record<
    string,
    'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple'
  > = {
    PENDIENTE: 'warning',
    APROBADA: 'success',
    RECHAZADA: 'danger',
    CANCELADA: 'default',
  }

  return map[s] ?? 'default'
}

export default function AsistenciaPage({ initialTab = 'registros' }: AsistenciaPageProps = {}) {
  const [tab, setTab] = useState<Tab>(initialTab)
  const { data: records = [], isLoading: loadR } = useAttendanceRecords()
  const { data: leaves  = [], isLoading: loadL } = useLeaveRequests()
  const reviewLeave  = useReviewLeave()
  const createLeave  = useCreateLeave()

  const [leaveForm, setLeaveForm] = useState({
    leave_type: 'VACACIONES' as LeaveType,
    start_date: '', end_date: '', reason: '', total_days: 1,
  })

  const submitLeave = () => {
    createLeave.mutate(leaveForm as any)
    setLeaveForm({ leave_type: 'VACACIONES', start_date: '', end_date: '', reason: '', total_days: 1 })
    setTab('permisos')
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'registros', label: 'Registro de asistencia' },
    { key: 'permisos',  label: 'Solicitudes de permiso' },
    { key: 'solicitar', label: '+ Solicitar permiso' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Control de Asistencia</h1>
        <p className="text-sm text-gray-500 mt-0.5">Entradas, salidas, vacaciones y licencias</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-gray-100 rounded-xl p-1 w-fit">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors
              ${tab === t.key ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Registros de asistencia */}
      {tab === 'registros' && (
        <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Registros de asistencia</h2>
          </div>
          {loadR ? (
            <div className="p-12 text-center text-gray-400">Cargando...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                  <tr>
                    {['Empleado','Fecha','Entrada','Salida','Horas','H. Extra','Retraso','Ausencia']
                      .map(h => <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {records.map(r => (
                    <tr key={r.id} className={`hover:bg-gray-50 ${r.isAbsence ? 'bg-red-50' : ''}`}>
                      <td className="px-4 py-3 font-medium">{r.employeeName}</td>
                      <td className="px-4 py-3 text-gray-600">{r.workDate}</td>
                      <td className="px-4 py-3 text-gray-600">
                        {r.checkIn ? new Date(r.checkIn).toLocaleTimeString('es-MX', {hour:'2-digit',minute:'2-digit'}) : '—'}
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {r.checkOut ? new Date(r.checkOut).toLocaleTimeString('es-MX', {hour:'2-digit',minute:'2-digit'}) : '—'}
                      </td>
                      <td className="px-4 py-3">{r.hoursWorked ?? '—'}</td>
                      <td className="px-4 py-3 text-blue-600">{r.extraHours > 0 ? `+${r.extraHours}h` : '—'}</td>
                      <td className="px-4 py-3 text-amber-600">
                        {r.lateMinutes > 0 ? `${r.lateMinutes} min` : '—'}
                      </td>
                      <td className="px-4 py-3">
                        {r.isAbsence ? <Badge variant="danger">Ausente</Badge> : <Badge variant="success">Presente</Badge>}
                      </td>
                    </tr>
                  ))}
                  {records.length === 0 && (
                    <tr><td colSpan={8} className="px-4 py-12 text-center text-gray-400">Sin registros.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Solicitudes de permiso */}
      {tab === 'permisos' && (
        <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Solicitudes de permiso y vacaciones</h2>
          </div>
          {loadL ? (
            <div className="p-12 text-center text-gray-400">Cargando...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                  <tr>
                    {['Empleado','Tipo','Inicio','Fin','Días','Razón','Estatus','Acciones']
                      .map(h => <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>)}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {leaves.map(l => (
                    <tr key={l.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 font-medium">{l.employeeName}</td>
                      <td className="px-4 py-3 text-gray-600">{l.leaveType}</td>
                      <td className="px-4 py-3 text-gray-600">{l.startDate}</td>
                      <td className="px-4 py-3 text-gray-600">{l.endDate}</td>
                      <td className="px-4 py-3">{l.totalDays}</td>
                      <td className="px-4 py-3 text-gray-600 max-w-xs truncate">{l.reason || '—'}</td>
                      <td className="px-4 py-3">
                        <Badge variant={statusBadge(l.status)}>{l.status}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        {l.status === 'PENDIENTE' && (
                          <div className="flex gap-1">
                            <Button size="sm"
                              loading={reviewLeave.isPending}
                              onClick={() => reviewLeave.mutate({ id: l.id, action: 'approve' })}>
                              ✓ Aprobar
                            </Button>
                            <Button size="sm" variant="danger"
                              loading={reviewLeave.isPending}
                              onClick={() => reviewLeave.mutate({ id: l.id, action: 'reject' })}>
                              ✗ Rechazar
                            </Button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                  {leaves.length === 0 && (
                    <tr><td colSpan={8} className="px-4 py-12 text-center text-gray-400">Sin solicitudes.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Solicitar permiso */}
      {tab === 'solicitar' && (
        <div className="bg-white border border-gray-100 rounded-xl p-6 max-w-xl space-y-4">
          <h2 className="font-semibold text-gray-900">Nueva solicitud de permiso</h2>
          <div>
            <label className="text-sm font-medium text-gray-700">Tipo de permiso</label>
            <select value={leaveForm.leave_type}
              onChange={e => setLeaveForm(f => ({...f, leave_type: e.target.value as LeaveType}))}
              className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm">
              <option value="VACACIONES">Vacaciones</option>
              <option value="PERSONAL">Permiso personal</option>
              <option value="MEDICO">Permiso médico</option>
              <option value="DUELO">Duelo</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Fecha inicio</label>
              <input type="date" value={leaveForm.start_date}
                onChange={e => setLeaveForm(f => ({...f, start_date: e.target.value}))}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"/>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Fecha fin</label>
              <input type="date" value={leaveForm.end_date}
                onChange={e => {
                  const days = leaveForm.start_date
                    ? Math.max(1, Math.round((new Date(e.target.value).getTime() - new Date(leaveForm.start_date).getTime()) / 86400000) + 1)
                    : 1
                  setLeaveForm(f => ({...f, end_date: e.target.value, total_days: days}))
                }}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"/>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">
              Días: <span className="text-blue-600 font-bold">{leaveForm.total_days}</span>
            </label>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Motivo (opcional)</label>
            <textarea rows={3} value={leaveForm.reason}
              onChange={e => setLeaveForm(f => ({...f, reason: e.target.value}))}
              className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none"
              placeholder="Describe brevemente el motivo del permiso..."/>
          </div>
          <div className="flex gap-2">
            <Button onClick={submitLeave} loading={createLeave.isPending}>
              Enviar solicitud
            </Button>
            <Button variant="secondary" onClick={() => setTab('permisos')}>Cancelar</Button>
          </div>
        </div>
      )}
    </div>
  )
}