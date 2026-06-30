export type DocumentCategory =
  | 'CONTRATO'
  | 'CERTIFICADO'
  | 'IDENTIFICACION'
  | 'COMPROBANTE_DOMICILIO'
  | 'CV'
  | 'TITULO_PROFESIONAL'
  | 'INCAPACIDAD'
  | 'OTRO'

export type DocumentStatus = 'VIGENTE' | 'POR_VENCER' | 'VENCIDO' | 'SIN_VENCIMIENTO'

export interface EmployeeDocument {
  id:            string
  employeeId:    string
  employeeName:  string
  category:      DocumentCategory
  title:         string
  fileName:      string
  fileSizeKB:    number
  mimeType:      string
  uploadedAt:    string
  uploadedBy:    string
  expiresAt:     string | null
  notes:         string
  url:           string
}

export interface DocumentCategoryInfo {
  value: DocumentCategory
  label: string
}

export const DOCUMENT_CATEGORIES: DocumentCategoryInfo[] = [
  { value: 'CONTRATO',              label: 'Contrato laboral' },
  { value: 'CERTIFICADO',           label: 'Certificado' },
  { value: 'IDENTIFICACION',        label: 'Identificación oficial' },
  { value: 'COMPROBANTE_DOMICILIO', label: 'Comprobante de domicilio' },
  { value: 'CV',                    label: 'Currículum' },
  { value: 'TITULO_PROFESIONAL',    label: 'Título profesional' },
  { value: 'INCAPACIDAD',           label: 'Incapacidad médica' },
  { value: 'OTRO',                  label: 'Otro' },
]
