import type { ICellRendererParams } from 'ag-grid-community'
import type { LancamentoFinanceiro } from '../../types/finance'

export function CategoriaFinanceiraCellRenderer(
  params: ICellRendererParams<LancamentoFinanceiro>,
) {
  if (!params.data?.categoria_nome) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <span className="inline-flex items-center gap-2 min-w-0">
      {params.data.categoria_cor_hex && (
        <span
          className="h-2.5 w-2.5 shrink-0 border border-gray-200"
          style={{ backgroundColor: params.data.categoria_cor_hex }}
        />
      )}
      <span className="truncate">{params.data.categoria_nome}</span>
    </span>
  )
}
