import type { ICellRendererParams } from 'ag-grid-community'
import { formatPercent } from '../../utils/format'

export function PercentCellRenderer(params: ICellRendererParams) {
  if (params.value === null || params.value === undefined) {
    return <span className="text-gray-400">—</span>
  }
  const num =
    typeof params.value === 'string' ? parseFloat(params.value) : params.value

  const colorClass =
    num >= 100 ? 'text-black' : num >= 50 ? 'text-gray-600' : 'text-gray-400'

  return (
    <span className={`font-mono tabular-nums font-medium ${colorClass}`}>
      {formatPercent(params.value)}
    </span>
  )
}
