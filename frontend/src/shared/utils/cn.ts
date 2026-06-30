// Utilidad para combinar clases de Tailwind de forma segura
export const cn = (...classes: (string | undefined | null | false)[]): string =>
  classes.filter(Boolean).join(' ')