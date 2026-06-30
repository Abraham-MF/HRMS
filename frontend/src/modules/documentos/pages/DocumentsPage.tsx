import { useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import {
  FileText, FileImage, Upload, Search, Trash2, Download,
  AlertTriangle, Clock, ShieldCheck, FolderOpen,
} from 'lucide-react'
import { Button } from '@/shared/components/ui/Button'
import { Badge } from '@/shared/components/ui/Badge'
import type { BadgeVariant } from '@/shared/components/ui/Badge'
import { useDocuments, useDeleteDocument } from '../hooks/useDocumentos'
import { UploadDocumentModal } from '../components/UploadDocumentModal'
import { DOCUMENT_CATEGORIES } from '@/types/documentos.types'
import type { EmployeeDocument, DocumentCategory, DocumentStatus } from '@/types/documentos.types'
import { formatDate } from '@/shared/utils/formateadores'
import toast from 'react-hot-toast'

function categoryLabel(category: DocumentCategory): string {
  return DOCUMENT_CATEGORIES.find(c => c.value === category)?.label ?? category
}

function getStatus(doc: EmployeeDocument): DocumentStatus {
  if (!doc.expiresAt) return 'SIN_VENCIMIENTO'
  const days = Math.ceil((new Date(doc.expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
  if (days < 0) return 'VENCIDO'
  if (days <= 30) return 'POR_VENCER'
  return 'VIGENTE'
}

function statusBadge(status: DocumentStatus): { variant: BadgeVariant; label: string } {
  const map: Record<DocumentStatus, { variant: BadgeVariant; label: string }> = {
    VIGENTE:         { variant: 'success', label: 'Vigente' },
    POR_VENCER:      { variant: 'warning', label: 'Por vencer' },
    VENCIDO:         { variant: 'danger',  label: 'Vencido' },
    SIN_VENCIMIENTO: { variant: 'default', label: 'Sin vencimiento' },
  }
  return map[status]
}

function fileIcon(mimeType: string) {
  if (mimeType.startsWith('image/')) return <FileImage size={20} className="text-purple-500" />
  return <FileText size={20} className="text-purple-500" />
}

function fmtSize(kb: number): string {
  if (kb < 1024) return `${kb} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

export default function DocumentsPage() {
  const [search, setSearch]     = useState('')
  const [category, setCategory] = useState<DocumentCategory | ''>('')
  const [showUpload, setShowUpload] = useState(false)
  const [toDelete, setToDelete] = useState<EmployeeDocument | null>(null)

  const { data: documents = [], isLoading } = useDocuments({ search, category })
  const remove = useDeleteDocument()

  const stats = useMemo(() => {
    const total      = documents.length
    const vencidos   = documents.filter(d => getStatus(d) === 'VENCIDO').length
    const porVencer  = documents.filter(d => getStatus(d) === 'POR_VENCER').length
    const vigentes   = total - vencidos - porVencer
    return { total, vencidos, porVencer, vigentes }
  }, [documents])

  const handleDelete = async () => {
    if (!toDelete) return
    try {
      await remove.mutateAsync(toDelete.id)
      toast.success('Documento eliminado.')
    } catch {
      toast.error('No se pudo eliminar el documento.')
    } finally {
      setToDelete(null)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Documentos</h1>
          <p className="text-sm text-zinc-400 mt-0.5">
            Almacenamiento de contratos, certificados y documentos del personal
          </p>
        </div>
        <Button onClick={() => setShowUpload(true)} icon={<Upload size={16} />}>
          Subir documento
        </Button>
      </div>

      {/* Resumen */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <StatCard icon={<FolderOpen size={18} />}    label="Total"       value={stats.total} />
        <StatCard icon={<ShieldCheck size={18} />}   label="Vigentes"    value={stats.vigentes}  tone="success" />
        <StatCard icon={<Clock size={18} />}         label="Por vencer"  value={stats.porVencer} tone="warning" />
        <StatCard icon={<AlertTriangle size={18} />} label="Vencidos"    value={stats.vencidos}  tone="danger" />
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-xl border border-gray-100 p-4 flex flex-wrap gap-3 items-center">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por título, empleado o archivo…"
            className="w-full pl-9 pr-3 py-2 border border-gray-200 rounded-lg text-sm"
          />
        </div>
        <select
          value={category}
          onChange={e => setCategory(e.target.value as DocumentCategory | '')}
          className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
        >
          <option value="">Todas las categorías</option>
          {DOCUMENT_CATEGORIES.map(c => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
      </div>

      {/* Lista de documentos */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
            Cargando documentos…
          </div>
        ) : documents.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-56 gap-3 text-gray-400">
            <FolderOpen size={40} strokeWidth={1.5} />
            <p className="text-sm font-medium">No se encontraron documentos</p>
            <p className="text-xs text-gray-300">Sube el primer documento del personal para comenzar</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wider">
                <tr>
                  {['Documento', 'Empleado', 'Categoría', 'Subido', 'Vencimiento', 'Estatus', ''].map(h => (
                    <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {documents.map(doc => {
                  const status = getStatus(doc)
                  const badge  = statusBadge(status)
                  return (
                    <tr key={doc.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {fileIcon(doc.mimeType)}
                          <div>
                            <p className="font-medium text-gray-900">{doc.title}</p>
                            <p className="text-xs text-gray-400">{doc.fileName} · {fmtSize(doc.fileSizeKB)}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-gray-700">{doc.employeeName}</td>
                      <td className="px-4 py-3">
                        <Badge variant="purple">{categoryLabel(doc.category)}</Badge>
                      </td>
                      <td className="px-4 py-3 text-gray-500">{formatDate(doc.uploadedAt)}</td>
                      <td className="px-4 py-3 text-gray-500">
                        {doc.expiresAt ? formatDate(doc.expiresAt) : '—'}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={badge.variant}>{badge.label}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1 justify-end">
                          <a
                            href={doc.url}
                            target="_blank"
                            rel="noreferrer"
                            title="Descargar"
                            className="p-2 rounded-lg text-gray-400 hover:text-purple-600 hover:bg-purple-50 transition-colors"
                          >
                            <Download size={16} />
                          </a>
                          <button
                            title="Eliminar"
                            onClick={() => setToDelete(doc)}
                            className="p-2 rounded-lg text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <UploadDocumentModal open={showUpload} onClose={() => setShowUpload(false)} />

      {/* Confirmación de borrado */}
      {toDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/40" onClick={() => setToDelete(null)} />
          <div className="relative bg-white rounded-xl shadow-xl w-full max-w-sm p-6 space-y-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-full bg-red-50 text-red-600"><AlertTriangle size={20} /></div>
              <h3 className="font-semibold text-gray-900">Eliminar documento</h3>
            </div>
            <p className="text-sm text-gray-600">
              ¿Seguro que quieres eliminar <span className="font-medium">{toDelete.title}</span>?
              Esta acción no se puede deshacer.
            </p>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => setToDelete(null)}>Cancelar</Button>
              <Button variant="danger" size="sm" onClick={handleDelete} loading={remove.isPending}>
                Eliminar
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function StatCard({
  icon, label, value, tone = 'default',
}: { icon: ReactNode; label: string; value: number; tone?: 'default' | 'success' | 'warning' | 'danger' }) {
  const toneClasses: Record<string, string> = {
    default: 'bg-zinc-800/60 text-zinc-300',
    success: 'bg-emerald-900/30 text-emerald-400',
    warning: 'bg-amber-900/30 text-amber-400',
    danger:  'bg-red-900/30 text-red-400',
  }
  return (
    <div className="bg-[#1c1c21] border border-zinc-800/60 rounded-xl p-4 flex items-center gap-3">
      <div className={`p-2.5 rounded-lg ${toneClasses[tone]}`}>{icon}</div>
      <div>
        <p className="text-xl font-bold text-white leading-none">{value}</p>
        <p className="text-xs text-zinc-500 mt-1">{label}</p>
      </div>
    </div>
  )
}
