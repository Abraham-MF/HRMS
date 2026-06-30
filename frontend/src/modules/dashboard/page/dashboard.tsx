import { useQuery } from '@tanstack/react-query'
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts'
import { Users, TrendingUp, Clock, AlertCircle } from 'lucide-react'
import apiClient from '@/shared/utils/api-client'
import { formatCurrency } from '@/shared/utils/formatters'

interface DashboardStats {
  totalEmployees:       number
  activeEmployees:      number
  newThisMonth:         number
  onLeaveToday:         number
  absencesToday:        number
  totalPayrollMonth:    number
  avgSalary:            number
  headcountByDept:      { name: string; count: number }[]
  attendanceLast7Days:  { date: string; present: number; absent: number }[]
  payrollLast6Months:   { month: string; total: number }[]
}

const KPICard = ({ title, value, subtitle, icon, color }: {
  title: string; value: string | number; subtitle?: string
  icon: React.ReactNode; color: string
}) => (
  <div className="bg-white rounded-xl border border-gray-100 p-5">
    <div className="flex items-start justify-between">
      <div className="space-y-1">
        <p className="text-sm text-gray-500">{title}</p>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
        {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}
      </div>
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        {icon}
      </div>
    </div>
  </div>
)

const DEPT_COLORS = ['#534AB7','#1D9E75','#D85A30','#BA7517','#888780']

export default function DashboardPage() {
  const { data: stats, isLoading } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats'],
    queryFn:  () => apiClient.get('/reports/dashboard/').then(r => r.data),
    refetchInterval: 60_000,  // refrescar cada minuto
  })

  if (isLoading) return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-pulse">
      {Array.from({length: 8}).map((_,i) => (
        <div key={i} className="h-28 bg-gray-100 rounded-xl"/>
      ))}
    </div>
  )

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Resumen de recursos humanos en tiempo real
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Empleados activos"
          value={stats?.activeEmployees ?? 0}
          subtitle={`de ${stats?.totalEmployees ?? 0} totales`}
          icon={<Users size={20} className="text-primary-600"/>}
          color="bg-primary-50"
        />
        <KPICard
          title="Altas este mes"
          value={stats?.newThisMonth ?? 0}
          icon={<TrendingUp size={20} className="text-emerald-600"/>}
          color="bg-emerald-50"
        />
        <KPICard
          title="En vacaciones hoy"
          value={stats?.onLeaveToday ?? 0}
          icon={<Clock size={20} className="text-amber-600"/>}
          color="bg-amber-50"
        />
        <KPICard
          title="Faltas hoy"
          value={stats?.absencesToday ?? 0}
          icon={<AlertCircle size={20} className="text-red-600"/>}
          color="bg-red-50"
        />
        <KPICard
          title="Nómina del mes"
          value={formatCurrency(stats?.totalPayrollMonth ?? 0)}
          subtitle="Total bruto"
          icon={<TrendingUp size={20} className="text-primary-600"/>}
          color="bg-primary-50"
        />
        <KPICard
          title="Salario promedio"
          value={formatCurrency(stats?.avgSalary ?? 0)}
          subtitle="Base mensual"
          icon={<Users size={20} className="text-emerald-600"/>}
          color="bg-emerald-50"
        />
      </div>

      {/* Gráficas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Asistencia últimos 7 días */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">
            Asistencia — últimos 7 días
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={stats?.attendanceLast7Days ?? []}
              margin={{top: 5, right: 10, bottom: 0, left: 0}}>
              <defs>
                <linearGradient id="present" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#534AB7" stopOpacity={0.15}/>
                  <stop offset="95%" stopColor="#534AB7" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="absent" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#D85A30" stopOpacity={0.15}/>
                  <stop offset="95%" stopColor="#D85A30" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0"/>
              <XAxis dataKey="date" tick={{fontSize: 11}} tickLine={false}/>
              <YAxis tick={{fontSize: 11}} tickLine={false} axisLine={false}/>
              <Tooltip contentStyle={{
                borderRadius: '8px', border: '1px solid #e5e7eb',
                fontSize: '12px'
              }}/>
              <Area type="monotone" dataKey="present" name="Presentes"
                stroke="#534AB7" fill="url(#present)" strokeWidth={2}/>
              <Area type="monotone" dataKey="absent" name="Ausentes"
                stroke="#D85A30" fill="url(#absent)" strokeWidth={2}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Headcount por departamento */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">
            Headcount por departamento
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={stats?.headcountByDept ?? []}
                cx="50%" cy="50%"
                innerRadius={55} outerRadius={85}
                dataKey="count" nameKey="name"
              >
                {(stats?.headcountByDept ?? []).map((_, i) => (
                  <Cell key={i} fill={DEPT_COLORS[i % DEPT_COLORS.length]}/>
                ))}
              </Pie>
              <Tooltip contentStyle={{
                borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '12px'
              }}/>
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-1">
            {(stats?.headcountByDept ?? []).slice(0, 5).map((d, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-full"
                    style={{background: DEPT_COLORS[i % DEPT_COLORS.length]}}/>
                  <span className="text-gray-600">{d.name}</span>
                </div>
                <span className="font-medium text-gray-900">{d.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Nómina últimos 6 meses */}
        <div className="lg:col-span-3 bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">
            Costo de nómina — últimos 6 meses
          </h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={stats?.payrollLast6Months ?? []}
              margin={{top: 5, right: 10, bottom: 0, left: 0}}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false}/>
              <XAxis dataKey="month" tick={{fontSize: 11}} tickLine={false}/>
              <YAxis tick={{fontSize: 11}} tickLine={false} axisLine={false}
                tickFormatter={v => `$${(v/1000).toFixed(0)}k`}/>
              <Tooltip
                formatter={(v) => [formatCurrency(Number(v ?? 0)), 'Total nómina']}
                contentStyle={{borderRadius:'8px', border:'1px solid #e5e7eb', fontSize:'12px'}}
              />
              <Bar dataKey="total" fill="#534AB7" radius={[4,4,0,0]}/>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}