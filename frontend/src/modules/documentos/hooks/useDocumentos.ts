import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { documentosApi } from '../api/documentos.api'
import type { DocumentFilters } from '../api/documentos.api'

export const DOCUMENTS_KEY = ['employee-documents']

export const useDocuments = (filters: DocumentFilters = {}) =>
  useQuery({
    queryKey: [...DOCUMENTS_KEY, filters],
    queryFn:  () => documentosApi.list(filters),
  })

export const useUploadDocument = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: documentosApi.upload,
    onSuccess:  () => qc.invalidateQueries({ queryKey: DOCUMENTS_KEY }),
  })
}

export const useDeleteDocument = () => {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: documentosApi.remove,
    onSuccess:  () => qc.invalidateQueries({ queryKey: DOCUMENTS_KEY }),
  })
}
