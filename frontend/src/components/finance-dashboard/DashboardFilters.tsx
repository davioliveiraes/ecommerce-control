interface Props {
  dataInicio: string
  dataFim: string
  incluirPendentes: boolean
  onDataInicioChange: (value: string) => void
  onDataFimChange: (value: string) => void
  onIncluirPendentesChange: (value: boolean) => void
  onClear: () => void
}

export function DashboardFilters({
  dataInicio,
  dataFim,
  incluirPendentes,
  onDataInicioChange,
  onDataFimChange,
  onIncluirPendentesChange,
  onClear,
}: Props) {
  return (
    <div className="border border-gray-200 bg-white px-4 py-3 flex flex-wrap items-end gap-3">
      <div>
        <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
          Início
        </label>
        <input
          type="date"
          value={dataInicio}
          onChange={(event) => onDataInicioChange(event.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors font-mono"
        />
      </div>

      <div>
        <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
          Fim
        </label>
        <input
          type="date"
          value={dataFim}
          onChange={(event) => onDataFimChange(event.target.value)}
          className="px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors font-mono"
        />
      </div>

      <label className="flex items-center gap-2 h-9 text-sm text-gray-600 select-none cursor-pointer">
        <input
          type="checkbox"
          checked={incluirPendentes}
          onChange={(event) => onIncluirPendentesChange(event.target.checked)}
          className="accent-black"
        />
        Incluir pendentes
      </label>

      <button
        type="button"
        onClick={onClear}
        className="h-9 px-3 text-sm border border-gray-200 text-gray-600 hover:text-black hover:border-gray-400 transition-colors"
      >
        Limpar filtros
      </button>

      <div className="ml-auto hidden md:block font-mono text-xs text-gray-600">
        {incluirPendentes ? 'visão competência' : 'somente pagos'}
      </div>
    </div>
  )
}
