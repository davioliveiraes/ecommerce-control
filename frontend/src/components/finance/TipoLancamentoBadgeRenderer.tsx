import type { ICellRendererParams } from 'ag-grid-community'
import type { LancamentoFinanceiro } from '../../types/finance'

const TIPO_LABELS = {
  RECEITA: { label: 'Entrada', detail: 'Receita', tone: 'text-navy bg-gray-50' },
  DESPESA: { label: 'Saída', detail: 'Despesa', tone: 'text-orange-dark bg-orange-soft' },
  CUSTO: { label: 'Saída', detail: 'Custo', tone: 'text-orange-dark bg-orange-soft' },
} as const

export function TipoLancamentoBadgeRenderer(
  params: ICellRendererParams<LancamentoFinanceiro>,
) {
  if (!params.data) return null

  const config = TIPO_LABELS[params.data.tipo]

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium ${config.tone}`}
    >
      <span>{config.label}</span>
      <span className="text-gray-400 font-mono uppercase">{config.detail}</span>
    </span>
  )
}
