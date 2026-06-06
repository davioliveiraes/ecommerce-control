import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ICellRendererParams } from 'ag-grid-community'
import type { Variacao } from '../../types/catalog'
import { archiveVariacao } from '../../api/variacoes'

export function AcoesCellRenderer(params: ICellRendererParams<Variacao>) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const archiveMutation = useMutation({
    mutationFn: archiveVariacao,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variacoes'] })
    },
  })

  if (!params.data) return null

  const handleEditar = () => {
    navigate(`/catalogo/produto/${params.data!.produto_id}`)
  }

  const handleArquivar = () => {
    const ref = params.data!.sku_nuvemshop || `#${params.data!.id}`
    if (confirm(`Arquivar variação ${ref}?`)) {
      archiveMutation.mutate(params.data!.id)
    }
  }

  return (
    <div className="flex items-center gap-1 h-full">
      <button
        onClick={handleEditar}
        className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-black hover:text-black hover:bg-gray-100 transition-colors cursor-pointer"
        title="Editar produto"
      >
        <IconPencil />
        Editar
      </button>
      <button
        onClick={handleArquivar}
        disabled={archiveMutation.isPending}
        className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-gray-600 hover:text-black hover:bg-gray-100 transition-colors disabled:opacity-50 cursor-pointer"
        title="Arquivar variação (soft delete)"
      >
        <IconArchive />
        Arquivar
      </button>
    </div>
  )
}

function IconPencil() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
    </svg>
  )
}

function IconArchive() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="5" />
      <path d="M4 8v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </svg>
  )
}
