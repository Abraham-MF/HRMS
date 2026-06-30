import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  plugins: [require('@tailwindcss/forms')],
} satisfies Config