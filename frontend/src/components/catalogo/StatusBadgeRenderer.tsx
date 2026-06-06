import type { ICellRendererParams } from 'ag-grid-community'

export function StatusBadgeRenderer(params: ICellRendererParams) {
  if (!params.value) return null
  const isAtivo = params.value === 'ATIVO'
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 text-xs font-medium border ${
        isAtivo
          ? 'border-black/30 text-black bg-black/[0.04]'
          : 'border-gray-200 text-gray-600 bg-gray-50'
      }`}
    >
      <span
        className={`h-1.5 w-1.5 rounded-full ${
          isAtivo ? 'bg-black' : 'bg-gray-400'
        }`}
      />
      {isAtivo ? 'Ativo' : 'Inativo'}
    </span>
  )
}
