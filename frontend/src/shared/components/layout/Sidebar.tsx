import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, Users, DollarSign, Clock, FileText,
  BarChart2, LogOut, X, Building2, Sparkles
} from 'lucide-react'
import { useAuthStore } from '@/modules/auth/store/authStore'
import type { UserRole } from '@/types/auth.types'
import { cn } from '@/shared/utils/cn'

interface NavItem {
  label: string
  to:    string
  icon:  React.ReactNode
  roles: UserRole[]
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',  to: '/dashboard',          icon: <LayoutDashboard size={18}/>, roles: ['ADMIN','HR','SUPERVISOR','EMPLOYEE'] },
  { label: 'Empleados',  to: '/employees',           icon: <Users size={18}/>,           roles: ['ADMIN','HR','SUPERVISOR'] },
  { label: 'Nómina',     to: '/payroll',             icon: <DollarSign size={18}/>,      roles: ['ADMIN','HR'] },
  { label: 'Asistencia', to: '/attendance',          icon: <Clock size={18}/>,           roles: ['ADMIN','HR','SUPERVISOR','EMPLOYEE'] },
  { label: 'Vacaciones', to: '/attendance/calendar', icon: <Building2 size={18}/>,       roles: ['ADMIN','HR','SUPERVISOR','EMPLOYEE'] },
  { label: 'Documentos', to: '/documents',           icon: <FileText size={18}/>,        roles: ['ADMIN','HR'] },
]

interface SidebarProps {
  open:    boolean
  onClose: () => void
}

export default function Sidebar({ open, onClose }: SidebarProps) {
  const { user, logout } = useAuthStore()

  const filteredNav = NAV_ITEMS.filter(item =>
    user && item.roles.includes(user.role)
  )

  const handleLogout = async () => {
    try {
      await fetch('/api/v1/auth/logout/', {
        method: 'POST',
        headers: { Authorization: `Bearer ${useAuthStore.getState().tokens?.access}` }
      })
    } finally {
      logout()
    }
  }

  return (
    <>
      {open && (
        <div className="fixed inset-0 bg-black/60 z-20 lg:hidden backdrop-blur-sm" onClick={onClose} />
      )}

      <aside className={cn(
        'fixed inset-y-0 left-0 z-30 w-64',
        'bg-[#1c1c21] border-r border-zinc-800/60',
        'transform transition-transform duration-300 ease-in-out',
        'flex flex-col lg:static lg:translate-x-0',
        open ? 'translate-x-0' : '-translate-x-full'
      )}>

        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-5 border-b border-zinc-800/60">
          <div className="flex items-center gap-3">
            <span className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center text-lg shadow-glow">
              🌊
            </span>
            <span className="font-bold text-white tracking-tight text-lg">
              Gestion RH 
            </span>
          </div>
          
          <button onClick={onClose} className="lg:hidden p-1 text-zinc-500 hover:text-white transition-colors">
            <X size={20} />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600 px-3 mb-3">
            Menú principal
          </p>
          {filteredNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={onClose}
              className={({ isActive }) => cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all duration-150',
                isActive
                  ? 'bg-purple-600/20 text-purple-300 font-medium border border-purple-700/40 shadow-glow'
                  : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-white'
              )}
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Usuario */}
        <div className="border-t border-zinc-800/60 px-3 py-4">
          <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl bg-zinc-800/40 mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-purple-900
              rounded-full flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
              {user?.username?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.username}</p>
              <p className="text-xs text-purple-400 truncate">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm
              text-zinc-500 hover:bg-red-900/20 hover:text-red-400
              transition-all duration-150 border border-transparent hover:border-red-900/40"
          >
            <LogOut size={16} />
            Cerrar sesión
          </button>
        </div>
      </aside>
    </>
  )
}
