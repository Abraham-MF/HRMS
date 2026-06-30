import { useState } from 'react'
import { Modal } from '@/shared/components/ui/Modal'
import { Button } from '@/shared/components/ui/Button'
import { DOCUMENT_CATEGORIES } from '@/types/documentos.types'
import type { DocumentCategory } from '@/types/documentos.types'
import { useEmployees } from '@/modules/empleados/hooks/useEmployees'
import { useUploadDocument } from '../hooks/useDocumentos'
import toast from 'react-hot-toast'

interface UploadDocumentModalProps {
  open:    boolean
  onClose: () => void
}

const MAX_SIZE_MB = 10

export function UploadDocumentModal({ open, onClose }: UploadDocumentModalProps) {
  const { data: employeesPage, isLoading: loadingEmployees } = useEmployees({ pageSize: 100 })
  const upload = useUploadDocument()

  const [employeeId, setEmployeeId] = useState('')
  const [category, setCategory]     = useState<DocumentCategory>('CONTRATO')
  const [title, setTitle]           = useState('')
  const [expiresAt, setExpiresAt]   = useState('')
  const [notes, setNotes]           = useState('')
  const [file, setFile]             = useState<File | null>(null)
  const [fileError, setFileError]   = useState('')

  const employees = employeesPage?.results ?? []

  const reset = () => {
    setEmployeeId(''); setCategory('CONTRATO'); setTitle('')
    setExpiresAt(''); setNotes(''); setFile(null); setFileError('')
  }

  const handleClose = () => { reset(); onClose() }

  const handleFile = (f: File | null) => {
    if (f && f.size > MAX_SIZE_MB * 1024 * 1024) {
      setFileError(`El archivo supera el límite de ${MAX_SIZE_MB} MB.`)
      setFile(null)
      return
    }
    setFileError('')
    setFile(f)
  }

  const canSubmit = !!employeeId && !!title.trim() && !!file && !upload.isPending

  const handleSubmit = async () => {
    if (!canSubmit || !file) return
    const employee = employees.find(e => e.id === employeeId)
    try {
      await upload.mutateAsync({
        employeeId,
        employeeName: employee?.fullName ?? '',
        category,
        title:     title.trim(),
        expiresAt: expiresAt || null,
        notes:     notes.trim(),
        file,
      })
      toast.success('Documento guardado correctamente.')
      handleClose()
    } catch {
      toast.error('No se pudo guardar el documento. Intenta de nuevo.')
    }
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title="Subir documento"
      size="md"
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={handleClose}>Cancelar</Button>
          <Button size="sm" onClick={handleSubmit} disabled={!canSubmit} loading={upload.isPending}>
            Guardar documento
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="text-sm font-medium text-gray-700">Empleado</label>
          <select
            value={employeeId}
            onChange={e => setEmployeeId(e.target.value)}
            disabled={loadingEmployees}
            className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Selecciona un empleado…</option>
            {employees.map(emp => (
              <option key={emp.id} value={emp.id}>{emp.fullName}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Categoría</label>
            <select
              value={category}
              onChange={e => setCategory(e.target.value as DocumentCategory)}
              className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              {DOCUMENT_CATEGORIES.map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Fecha de vencimiento</label>
            <input
              type="date"
              value={expiresAt}
              onChange={e => setExpiresAt(e.target.value)}
              className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
            />
            <p className="text-xs text-gray-400 mt-1">Déjalo vacío si el documento no vence.</p>
          </div>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700">Título del documento</label>
          <input
            type="text"
            value={title}
            onChange={e => setTitle(e.target.value)}
            placeholder="Ej. Contrato indefinido 2026"
            className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
          />
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700">Archivo</label>
          <input
            type="file"
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            onChange={e => handleFile(e.target.files?.[0] ?? null)}
            className="mt-1 w-full text-sm text-gray-600
              file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0
              file:text-sm file:font-medium file:bg-purple-50 file:text-purple-700
              hover:file:bg-purple-100 border border-gray-200 rounded-lg"
          />
          {fileError && <p className="text-xs text-red-600 mt-1">{fileError}</p>}
          <p className="text-xs text-gray-400 mt-1">PDF, JPG, PNG o Word · máximo {MAX_SIZE_MB} MB.</p>
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700">Notas (opcional)</label>
          <textarea
            value={notes}
            onChange={e => setNotes(e.target.value)}
            rows={2}
            placeholder="Información adicional sobre este documento…"
            className="mt-1 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm resize-none"
          />
        </div>
      </div>
    </Modal>
  )
}
