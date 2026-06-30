import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'

export const formatDate = (dateStr: string): string => {
  if (!dateStr) return '—'
  try {
    return format(parseISO(dateStr), 'd MMM yyyy', { locale: es })
  } catch {
    return dateStr
  }
}

export const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '—'
  try {
    return format(parseISO(dateStr), "d MMM yyyy 'a las' HH:mm", { locale: es })
  } catch {
    return dateStr
  }
}

export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style:    'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
  }).format(amount)
}

export const formatCURP = (curp: string): string =>
  curp?.toUpperCase() ?? ''

export const formatRFC = (rfc: string): string =>
  rfc?.toUpperCase() ?? ''