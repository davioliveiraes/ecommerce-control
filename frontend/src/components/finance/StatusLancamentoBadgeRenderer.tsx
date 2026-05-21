import type { ICellRendererParams } from 'ag-grid-community'
import type { LancamentoFinanceiro } from '../../types/finance'

export function StatusLancamentoBadgeRenderer(
  params: ICellRendererParams<LancamentoFinanceiro>,
) {
  if (!params.data) return null

  const status = !params.data.ativo ? 'ARQUIVADO' : params.data.status
  const className =
    status === 'PAGO'
      ? 'bg-gray-50 text-navy'
      : status === 'ARQUIVADO'
        ? 'bg-gray-100 text-gray-600'
        : 'bg-orange-soft text-orange-dark'

  const label =
    status === 'PAGO'
      ? 'Pago'
      : status === 'ARQUIVADO'
        ? 'Arquivado'
        : 'Pendente'

  return (
    <span
      className={`inline-flex items-center px-2 py-1 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  )
}
