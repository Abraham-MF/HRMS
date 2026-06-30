import { useState } from 'react'
import { usePayrollPeriods, usePayrollRecords,
         useCalculatePeriod, useApprovePeriod, usePayPeriod } from '../hooks/useNominas'
import { nominasApi } from '../api/nominas.api'
import type { PayrollPeriod } from '@/types/nominas.types'
import { Button } from '@/shared/components/ui/Button'
import { Badge } from '@/shared/components/ui/Badge'
import { useQueryClient } from '@tanstack/react-query'
import { PERIODS_KEY } from '../hooks/useNominas'
import type { BadgeVariant } from '@/shared/components/ui/Badge'

function statusBadge(s: string): BadgeVariant {
  const map: Record<string, BadgeVariant> = {
    ABIERTO: 'info',
    CERRADO: 'default',
    PAGADO: 'success',
    CALCULADO: 'info',
    APROBADO: 'default',
    CANCELADO: 'danger',
  }

  return map[s] ?? 'default'
}

function fmt(n: number) {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(n)
}

export default function NominasPage() {
  const { data: periods = [], isLoading } = usePayrollPeriods()
  const [selected, setSelected]   = useState<PayrollPeriod | null>(null)
  const [showForm, setShowForm]   = useState(false)
  const { data: records = [] }     = usePayrollRecords(selected?.id)
  const calculate  = useCalculatePeriod()
  const approve    = useApprovePeriod()
  const pay        = usePayPeriod()
  const qc         = useQueryClient()

  const [form, setForm] = useState({
    period_type: 'QUINCENAL', start_date: '', end_date: ''
  })

  const createPeriod = async () => {
    await nominasApi.createPeriod(form as any)
    qc.invalidateQueries({ queryKey: PERIODS_KEY })
    setShowForm(false)
    setForm({ period_type: 'QUINCENAL', start_date: '', end_date: '' })
  }

  if (isLoading) return (
    <div className="flex items-center justify-center h-64 text-gray-500">Cargando nóminas...</div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Nóminas</h1>
          <p className="text-sm text-gray-500 mt-0.5">Cálculo automático ISR 2024 · IMSS · INFONAVIT</p>
        </div>
        <Button onClick={() => setShowForm(true)}>+ Nuevo periodo</Button>
      </div>

      {/* Formulario nuevo periodo */}
      {showForm && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-4">
          <h3 className="font-semibold text-blue-900">Crear periodo de nómina</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Tipo</label>
              <select value={form.period_type}
                onChange={e => setForm(f => ({...f, period_type: e.target.value}))}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm">
                <option value="SEMANAL">Semanal</option>
                <option value="QUINCENAL">Quincenal</option>
                <option value="MENSUAL">Mensual</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Inicio</label>
              <input type="date" value={form.start_date}
                onChange={e => setForm(f => ({...f, start_date: e.target.value}))}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"/>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Fin</label>
              <input type="date" value={form.end_date}
                onChange={e => setForm(f => ({...f, end_date: e.target.value}))}
                className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"/>
            </div>
          </div>
          <div className="flex gap-2">
            <Button onClick={createPeriod} size="sm">Crear</Button>
            <Button variant="secondary" size="sm" onClick={() => setShowForm(false)}>Cancelar</Button>
          </div>
        </div>
      )}

      {/* Lista de periodos */}
      <div className="grid grid-cols-1 gap-3">
        {periods.map(p => (
          <div key={p.id}
            onClick={() => setSelected(selected?.id === p.id ? null : p)}
            className={`bg-white border rounded-xl p-4 cursor-pointer transition-all
              ${selected?.id === p.id ? 'border-blue-400 shadow-md' : 'border-gray-100 hover:border-gray-300'}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="text-sm font-semibold text-gray-900">
                  {p.periodType} · {p.startDate} – {p.endDate}
                </div>
                <Badge variant={statusBadge(p.status)}>{p.status}</Badge>
              </div>
              <div className="flex gap-2" onClick={e => e.stopPropagation()}>
                {p.status === 'ABIERTO' && (
                  <Button size="sm" onClick={() => calculate.mutate(p.id)}
                    loading={calculate.isPending}>
                    Calcular
                  </Button>
                )}
                {p.status === 'ABIERTO' && (
                  <Button size="sm" variant="secondary" onClick={() => approve.mutate(p.id)}
                    loading={approve.isPending}>
                    Aprobar todos
                  </Button>
                )}
                {p.status !== 'PAGADO' && (
                  <Button size="sm" variant="danger" onClick={() => pay.mutate(p.id)}
                    loading={pay.isPending}>
                    Pagar
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}
        {periods.length === 0 && (
          <p className="text-center text-gray-400 py-12">No hay periodos de nómina creados.</p>
        )}
      </div>

      {/* Recibos del periodo seleccionado */}
      {selected && records.length > 0 && (
        <div className="bg-white border border-gray-100 rounded-xl overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">
              Recibos — {selected.periodType} {selected.startDate} al {selected.endDate}
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
                <tr>
                  {['Empleado','Salario base','Horas extra','Bruto','ISR','IMSS','INFONAVIT','Deduc. total','Neto','Estatus']
                    .map(h => <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>)}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {records.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{r.employeeName}</td>
                    <td className="px-4 py-3 text-gray-600">{fmt(r.baseSalary)}</td>
                    <td className="px-4 py-3 text-gray-600">{fmt(r.extraHoursAmount)}</td>
                    <td className="px-4 py-3 font-medium">{fmt(r.grossSalary)}</td>
                    <td className="px-4 py-3 text-red-600">{fmt(r.isrDeduction)}</td>
                    <td className="px-4 py-3 text-red-600">{fmt(r.imssDeduction)}</td>
                    <td className="px-4 py-3 text-red-600">{fmt(r.infonavitDeduction)}</td>
                    <td className="px-4 py-3 text-red-700 font-medium">{fmt(r.totalDeductions)}</td>
                    <td className="px-4 py-3 text-green-700 font-bold">{fmt(r.netSalary)}</td>
                    <td className="px-4 py-3"><Badge variant={statusBadge(r.status)}>{r.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
              <tfoot className="bg-gray-50 font-semibold text-sm">
                <tr>
                  <td className="px-4 py-3 text-gray-700">TOTAL</td>
                  <td className="px-4 py-3">{fmt(records.reduce((s,r)=>s+r.baseSalary,0))}</td>
                  <td/>
                  <td className="px-4 py-3">{fmt(records.reduce((s,r)=>s+r.grossSalary,0))}</td>
                  <td className="px-4 py-3 text-red-600">{fmt(records.reduce((s,r)=>s+r.isrDeduction,0))}</td>
                  <td className="px-4 py-3 text-red-600">{fmt(records.reduce((s,r)=>s+r.imssDeduction,0))}</td>
                  <td className="px-4 py-3 text-red-600">{fmt(records.reduce((s,r)=>s+r.infonavitDeduction,0))}</td>
                  <td className="px-4 py-3 text-red-700">{fmt(records.reduce((s,r)=>s+r.totalDeductions,0))}</td>
                  <td className="px-4 py-3 text-green-700">{fmt(records.reduce((s,r)=>s+r.netSalary,0))}</td>
                  <td/>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
