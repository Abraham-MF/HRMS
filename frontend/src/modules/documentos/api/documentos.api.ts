import apiClient from '@/shared/utils/api-client'
import type { EmployeeDocument, DocumentCategory } from '@/types/documentos.types'

const BASE = '/documents'

// ── Almacén simulado en memoria ──────────────────────────────────────────────
// Se usa como respaldo automático mientras el backend de Django no expone
// todavía el endpoint /api/v1/documents/. En cuanto el endpoint real responda,
// la API deja de usar este respaldo. Esto permite que la pantalla sea
// funcional desde ya y no bloquea el desarrollo del backend.
let mockSeeded = false
let mockStore: EmployeeDocument[] = []

function seedMockStore() {
  if (mockSeeded) return
  mockSeeded = true
  const today = new Date()
  const inDays = (n: number) => {
    const d = new Date(today)
    d.setDate(d.getDate() + n)
    return d.toISOString().slice(0, 10)
  }
  mockStore = [
    {
      id: 'doc-1', employeeId: 'emp-1', employeeName: 'Ana López Hernández',
      category: 'CONTRATO', title: 'Contrato indefinido 2024',
      fileName: 'contrato_ana_lopez.pdf', fileSizeKB: 482, mimeType: 'application/pdf',
      uploadedAt: inDays(-200), uploadedBy: 'admin', expiresAt: null,
      notes: 'Contrato vigente sin fecha de término.', url: '#',
    },
    {
      id: 'doc-2', employeeId: 'emp-2', employeeName: 'Carlos Ramírez Díaz',
      category: 'IDENTIFICACION', title: 'INE vigente',
      fileName: 'ine_carlos_ramirez.jpg', fileSizeKB: 210, mimeType: 'image/jpeg',
      uploadedAt: inDays(-30), uploadedBy: 'rh.maria', expiresAt: inDays(20),
      notes: '', url: '#',
    },
    {
      id: 'doc-3', employeeId: 'emp-3', employeeName: 'Sofía Martínez Ruiz',
      category: 'CERTIFICADO', title: 'Certificado de seguridad e higiene',
      fileName: 'certificado_seguridad_sofia.pdf', fileSizeKB: 134, mimeType: 'application/pdf',
      uploadedAt: inDays(-400), uploadedBy: 'admin', expiresAt: inDays(-5),
      notes: 'Renovación pendiente con el organismo certificador.', url: '#',
    },
    {
      id: 'doc-4', employeeId: 'emp-1', employeeName: 'Ana López Hernández',
      category: 'COMPROBANTE_DOMICILIO', title: 'Comprobante de domicilio CFE',
      fileName: 'cfe_ana_lopez.pdf', fileSizeKB: 98, mimeType: 'application/pdf',
      uploadedAt: inDays(-15), uploadedBy: 'rh.maria', expiresAt: null,
      notes: '', url: '#',
    },
    {
      id: 'doc-5', employeeId: 'emp-4', employeeName: 'Jorge Pérez Castillo',
      category: 'TITULO_PROFESIONAL', title: 'Título de Ingeniería Industrial',
      fileName: 'titulo_jorge_perez.pdf', fileSizeKB: 760, mimeType: 'application/pdf',
      uploadedAt: inDays(-600), uploadedBy: 'admin', expiresAt: null,
      notes: '', url: '#',
    },
  ]
}

function useMock(error: unknown): boolean {
  // 404 o error de red ⇒ el endpoint todavía no existe en el backend
  const status = (error as { response?: { status?: number } })?.response?.status
  return status === 404 || status === undefined
}

export interface DocumentFilters {
  search?:     string
  employeeId?: string
  category?:   DocumentCategory | ''
  status?:     'VIGENTE' | 'POR_VENCER' | 'VENCIDO' | ''
}

export const documentosApi = {
  list: async (filters: DocumentFilters = {}): Promise<EmployeeDocument[]> => {
    try {
      const { data } = await apiClient.get<{ results: EmployeeDocument[] }>(`${BASE}/`, { params: filters })
      return data.results
    } catch (error) {
      if (!useMock(error)) throw error
      seedMockStore()
      let results = [...mockStore]
      if (filters.employeeId) results = results.filter(d => d.employeeId === filters.employeeId)
      if (filters.category)   results = results.filter(d => d.category === filters.category)
      if (filters.search) {
        const q = filters.search.toLowerCase()
        results = results.filter(d =>
          d.title.toLowerCase().includes(q) ||
          d.employeeName.toLowerCase().includes(q) ||
          d.fileName.toLowerCase().includes(q)
        )
      }
      return results.sort((a, b) => b.uploadedAt.localeCompare(a.uploadedAt))
    }
  },

  upload: async (data: Omit<EmployeeDocument, 'id' | 'uploadedAt' | 'uploadedBy' | 'url' | 'fileSizeKB' | 'mimeType' | 'fileName'> & { file: File }): Promise<EmployeeDocument> => {
    try {
      const form = new FormData()
      Object.entries(data).forEach(([k, v]) => {
        if (v !== null && v !== undefined) form.append(k, v as string | Blob)
      })
      const { data: created } = await apiClient.post<EmployeeDocument>(`${BASE}/`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return created
    } catch (error) {
      if (!useMock(error)) throw error
      seedMockStore()
      const created: EmployeeDocument = {
        id:           `doc-${Date.now()}`,
        employeeId:   data.employeeId,
        employeeName: data.employeeName,
        category:     data.category,
        title:        data.title,
        fileName:     data.file.name,
        fileSizeKB:   Math.max(1, Math.round(data.file.size / 1024)),
        mimeType:     data.file.type || 'application/octet-stream',
        uploadedAt:   new Date().toISOString().slice(0, 10),
        uploadedBy:   'tú',
        expiresAt:    data.expiresAt,
        notes:        data.notes,
        url:          '#',
      }
      mockStore = [created, ...mockStore]
      return created
    }
  },

  remove: async (id: string): Promise<void> => {
    try {
      await apiClient.delete(`${BASE}/${id}/`)
    } catch (error) {
      if (!useMock(error)) throw error
      seedMockStore()
      mockStore = mockStore.filter(d => d.id !== id)
    }
  },
}
