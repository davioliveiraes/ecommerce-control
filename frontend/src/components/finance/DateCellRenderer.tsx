import type { ICellRendererParams } from 'ag-grid-community'

export function DateCellRenderer(params: ICellRendererParams) {
  if (!params.value) {
    return <span className="text-gray-400">—</span>
  }

  const date = new Date(`${params.value}T00:00:00`)
  if (isNaN(date.getTime())) {
    return <span className="text-gray-400">—</span>
  }

  return (
    <span className="font-mono text-xs tabular-nums">
      {new Intl.DateTimeFormat('pt-BR').format(date)}
    </span>
  )
}
