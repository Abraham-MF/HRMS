import React from 'react'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info' | 'purple'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'bg-zinc-800 text-zinc-400 border-zinc-700',
  success: 'bg-emerald-900/40 text-emerald-400 border-emerald-800/50',
  warning: 'bg-amber-900/40 text-amber-400 border-amber-800/50',
  danger:  'bg-red-900/40 text-red-400 border-red-800/50',
  info:    'bg-blue-900/40 text-blue-400 border-blue-800/50',
  purple:  'bg-purple-900/40 text-purple-400 border-purple-800/50',
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variantClasses[variant]} ${className}`}>
      {children}
    </span>
  )
}

export function employeeStatusBadge(status: string): BadgeVariant {
  const map: Record<string, BadgeVariant> = {
    ACTIVO:     'success',
    INACTIVO:   'danger',
    SUSPENDIDO: 'warning',
    BAJA:       'danger',
    VACACIONES: 'purple',
  }
  return map[status] ?? 'default'
}
