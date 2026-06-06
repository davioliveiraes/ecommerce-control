import { useState } from 'react'
import type {
  CategoriaFinanceira,
  FinanceFatiaCategoria,
  FinancePeriodoCategoria,
  TipoLancamento,
} from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface CategoryPieChartProps {
  receitas: FinanceFatiaCategoria[]
  despesas: FinanceFatiaCategoria[]
  custos: FinanceFatiaCategoria[]
}

interface CategoryFiltersPanelProps extends CategoryPieChartProps {
  categorias: CategoriaFinanceira[]
  periodosPorCategoria: FinancePeriodoCategoria[]
  selectedCategoriaId: number | null
  onCategoriaChange: (
    categoriaId: number | null,
    periodo?: FinancePeriodoCategoria,
  ) => void
  selectedTipo: TipoLancamento | ''
  onTipoChange: (tipo: TipoLancamento | '') => void
}

interface Slice {
  label: string
  entrada: number
  saida: number
  total: number
  color: string
}

const FALLBACK_COLORS = [
  '#0a0a0a',
  '#404040',
  '#737373',
  '#a3a3a3',
  '#525252',
  '#262626',
]

const CATEGORY_KIND_BY_SLUG: Record<string, TipoLancamento> = {
  'vendas-nuvemshop': 'RECEITA',
  'nuvemshop-plano': 'DESPESA',
  'hospedagem-dominio': 'DESPESA',
  'email-profissional': 'DESPESA',
  'equipe-ecommerce': 'DESPESA',
  'marketing-trafego': 'DESPESA',
  'taxas-meios-pagamento': 'DESPESA',
  'embalagens-frete': 'CUSTO',
}

const TYPE_LABELS: Record<TipoLancamento, string> = {
  RECEITA: 'Entrada',
  DESPESA: 'Saída',
  CUSTO: 'Custo',
}

export function CategoryPieChart({
  receitas,
  despesas,
  custos,
}: CategoryPieChartProps) {
  const slices = buildSlices(receitas, despesas, custos)
  const totalMovimentado = slices.reduce((acc, slice) => acc + slice.total, 0)

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="mb-5">
        <div className="kicker mb-1">Categorias</div>
        <h2 className="font-display text-xl font-semibold text-black">
          Categorias financeiras
        </h2>
        <p className="mt-1 text-sm text-gray-600">
          Distribuição de entradas e saídas por categoria.
        </p>
      </div>

      {slices.length === 0 ? (
        <div className="h-[300px] border border-dashed border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
          Sem categorias no período selecionado.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[280px_minmax(0,1fr)] gap-6 items-center">
          <CategoryDonut slices={slices} totalMovimentado={totalMovimentado} />

          <CategoryLegend
            slices={slices}
            totalMovimentado={totalMovimentado}
          />
        </div>
      )}
    </section>
  )
}

export function CategoryFiltersPanel({
  receitas,
  despesas,
  custos,
  categorias,
  periodosPorCategoria,
  selectedCategoriaId,
  onCategoriaChange,
  selectedTipo,
  onTipoChange,
}: CategoryFiltersPanelProps) {
  const slices = buildSlices(receitas, despesas, custos)
  const totalEntradas = slices.reduce((acc, slice) => acc + slice.entrada, 0)
  const totalSaidas = slices.reduce((acc, slice) => acc + slice.saida, 0)
  const activeCategorias = categorias.filter((categoria) => categoria.ativo)
  const selectedCategoria = activeCategorias.find(
    (categoria) => categoria.id === selectedCategoriaId,
  )
  const lockedTipo = selectedCategoria
    ? CATEGORY_KIND_BY_SLUG[selectedCategoria.slug]
    : null

  const handleCategoriaChange = (categoria: CategoriaFinanceira | null) => {
    const periodo = periodosPorCategoria.find(
      (item) => item.categoria_id === (categoria?.id ?? null),
    )
    onCategoriaChange(categoria?.id ?? null, periodo)
    const tipo = categoria ? CATEGORY_KIND_BY_SLUG[categoria.slug] : null
    if (tipo) {
      onTipoChange(tipo)
    } else {
      onTipoChange('')
    }
  }

  return (
    <aside className="flex h-full flex-col border border-gray-200 bg-white p-5">
      <div className="mb-6">
        <div className="kicker mb-1">Filtro</div>
        <h2 className="font-display text-xl font-semibold text-black">
          Filtros
        </h2>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
            Categoria
          </label>
          <div className="max-h-[360px] overflow-y-auto border border-gray-200">
            <CategoryOption
              label="Todas as categorias"
              active={selectedCategoriaId === null}
              onClick={() => handleCategoriaChange(null)}
            />

            {activeCategorias.map((categoria) => (
              <CategoryOption
                key={categoria.id}
                label={categoria.nome}
                kind={CATEGORY_KIND_BY_SLUG[categoria.slug]}
                active={selectedCategoriaId === categoria.id}
                onClick={() => handleCategoriaChange(categoria)}
              />
            ))}
          </div>
        </div>

        <div>
          <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
            Tipo
          </label>
          <div className="border border-gray-200 text-sm">
            <TypeFilterButton
              label="Todos"
              active={selectedTipo === ''}
              onClick={() => onTipoChange('')}
              disabled={!!lockedTipo}
            />
            <TypeFilterButton
              label="Entrada"
              active={selectedTipo === 'RECEITA'}
              onClick={() => onTipoChange('RECEITA')}
              disabled={!!lockedTipo && lockedTipo !== 'RECEITA'}
            />
            <TypeFilterButton
              label="Saída"
              active={selectedTipo === 'DESPESA'}
              onClick={() => onTipoChange('DESPESA')}
              disabled={!!lockedTipo && lockedTipo !== 'DESPESA'}
            />
            <TypeFilterButton
              label="Custo"
              active={selectedTipo === 'CUSTO'}
              onClick={() => onTipoChange('CUSTO')}
              disabled={!!lockedTipo && lockedTipo !== 'CUSTO'}
            />
          </div>
          {lockedTipo && (
            <p className="mt-2 text-xs text-gray-600">
              Categoria travada como {TYPE_LABELS[lockedTipo].toLowerCase()}.
            </p>
          )}
        </div>
      </div>

      <div className="mt-auto border-t border-gray-100 pt-5">
        <div className="kicker mb-3">Valores</div>
        <div className="space-y-2">
            <SummaryRow
              label="Entrada"
              value={formatCurrency(totalEntradas)}
              className="text-black"
            />
            <SummaryRow
              label="Saída"
              value={formatCurrency(totalSaidas)}
              className="text-gray-700"
            />
        </div>
      </div>
    </aside>
  )
}

function CategoryDonut({
  slices,
  totalMovimentado,
}: {
  slices: Slice[]
  totalMovimentado: number
}) {
  const [hover, setHover] = useState<{
    slice: Slice
    percentual: number
  } | null>(null)

  return (
    <div className="relative w-full max-w-[280px] mx-auto">
      <svg
        viewBox="0 0 220 220"
        role="img"
        aria-label="Distribuição financeira por categoria"
        className="w-full"
      >
        <circle cx="110" cy="110" r="76" fill="#fafafa" />
        {slices.map((slice, index) => {
          const dashArray = `${(slice.total / totalMovimentado) * 100} ${
            100 - (slice.total / totalMovimentado) * 100
          }`
          const offset =
            -slices
              .slice(0, index)
              .reduce(
                (acc, item) => acc + (item.total / totalMovimentado) * 100,
                0,
              ) + 25

          const percentual = (slice.total / totalMovimentado) * 100
          return (
            <circle
              key={slice.label}
              cx="110"
              cy="110"
              r="76"
              fill="transparent"
              stroke={slice.color}
              strokeWidth="34"
              strokeDasharray={dashArray}
              strokeDashoffset={offset}
              pathLength="100"
              style={{ cursor: 'pointer' }}
              onMouseEnter={() => setHover({ slice, percentual })}
              onMouseLeave={() => setHover(null)}
            />
          )
        })}
        <circle cx="110" cy="110" r="48" fill="white" pointerEvents="none" />
        <text
          x="110"
          y="105"
          textAnchor="middle"
          className="fill-gray-600"
          fontSize="11"
          fontFamily="monospace"
          pointerEvents="none"
        >
          categorias
        </text>
        <text
          x="110"
          y="124"
          textAnchor="middle"
          className="fill-black"
          fontSize="14"
          fontFamily="monospace"
          pointerEvents="none"
        >
          {slices.length}
        </text>
      </svg>

      {hover && (
        <div className="pointer-events-none absolute left-1/2 top-1/2 z-10 -translate-x-1/2 -translate-y-1/2 border border-black bg-white px-3 py-2 shadow-lg min-w-[160px]">
          <div className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-wider text-gray-600">
            <span
              className="h-2 w-2"
              style={{ backgroundColor: hover.slice.color }}
            />
            {hover.slice.label}
          </div>
          <div className="mt-1 font-mono text-sm font-semibold tabular-nums text-black">
            {formatCurrency(hover.slice.total)}
          </div>
          <div className="font-mono text-[11px] tabular-nums text-gray-600">
            {hover.percentual.toFixed(1).replace('.', ',')}% do total
          </div>
        </div>
      )}
    </div>
  )
}

function CategoryLegend({
  slices,
  totalMovimentado,
}: {
  slices: Slice[]
  totalMovimentado: number
}) {
  return (
    <div className="grid min-w-0 grid-cols-1 md:grid-cols-2 gap-x-5 gap-y-3">
      {slices.map((slice) => (
        <div
          key={slice.label}
          className="min-w-0 border-b border-gray-100 pb-3 last:border-b-0 md:[&:nth-last-child(-n+2)]:border-b-0"
        >
          <div className="flex items-start gap-2.5 min-w-0">
            <span
              className="mt-1.5 h-2.5 w-2.5 shrink-0"
              style={{ backgroundColor: slice.color }}
            />
            <span className="min-w-0 text-sm font-medium leading-snug text-black break-words">
              {slice.label}
            </span>
          </div>

          <div
            className="mt-2 h-1.5 bg-gray-100"
            title={`${slice.label}: ${formatCurrency(slice.total)} (${((slice.total / totalMovimentado) * 100).toFixed(1).replace('.', ',')}% do total)`}
          >
            <div
              className="h-full"
              style={{
                width: `${(slice.total / totalMovimentado) * 100}%`,
                backgroundColor: slice.color,
              }}
            />
          </div>

          <div className="mt-2 space-y-1.5 rounded-sm bg-gray-50 px-2.5 py-2">
            {slice.entrada > 0 && (
              <LegendAmountRow
                label="Entrada"
                value={`+ ${formatCurrency(slice.entrada)}`}
                className="text-black"
              />
            )}
            {slice.saida > 0 && (
              <LegendAmountRow
                label="Saída"
                value={`- ${formatCurrency(slice.saida)}`}
                className="text-gray-700"
              />
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function LegendAmountRow({
  label,
  value,
  className,
}: {
  label: string
  value: string
  className: string
}) {
  return (
    <div className="grid min-w-0 grid-cols-[72px_minmax(0,1fr)] items-baseline gap-2 text-xs">
      <span className="text-gray-500">{label}</span>
      <span
        className={`min-w-0 overflow-hidden text-ellipsis text-right font-mono tabular-nums whitespace-nowrap ${className}`}
      >
        {value}
      </span>
    </div>
  )
}

function SummaryRow({
  label,
  value,
  className,
}: {
  label: string
  value: string
  className: string
}) {
  return (
    <div className="flex items-baseline justify-between gap-3">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`font-mono text-sm tabular-nums ${className}`}>
        {value}
      </span>
    </div>
  )
}

function CategoryOption({
  label,
  kind,
  active,
  onClick,
}: {
  label: string
  kind?: TipoLancamento
  active: boolean
  onClick: () => void
}) {
  const accentColor = kind ? '#0a0a0a' : '#d4d4d4'

  return (
    <button
      type="button"
      role="option"
      aria-selected={active}
      onClick={onClick}
      className={`flex w-full items-stretch gap-3 px-3 py-2 text-left text-sm transition-colors ${
        active
          ? 'bg-black text-white'
          : 'text-gray-700 hover:bg-gray-50 hover:text-black'
      }`}
    >
      <span
        className="w-1 shrink-0 self-stretch"
        style={{ backgroundColor: accentColor }}
      />
      <span className="min-w-0 flex-1">
        <span className="block leading-snug">{label}</span>
        {kind && (
          <span className="mt-0.5 block font-mono text-[10px] uppercase tracking-wider text-gray-500">
            {TYPE_LABELS[kind]}
          </span>
        )}
      </span>
    </button>
  )
}

function TypeFilterButton({
  label,
  active,
  disabled,
  onClick,
}: {
  label: string
  active: boolean
  disabled?: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`block w-full border-b border-gray-200 px-3 py-2 text-left transition-colors last:border-b-0 disabled:cursor-not-allowed disabled:opacity-35 ${
        active
          ? 'bg-black text-white'
          : 'bg-white text-gray-700 hover:bg-gray-50 hover:text-black'
      }`}
    >
      {label}
    </button>
  )
}

function buildSlices(
  receitas: FinanceFatiaCategoria[],
  despesas: FinanceFatiaCategoria[],
  custos: FinanceFatiaCategoria[],
): Slice[] {
  const map = new Map<string, Slice>()

  const addItem = (
    item: FinanceFatiaCategoria,
    index: number,
    field: 'entrada' | 'saida',
  ) => {
    const label = item.categoria_nome || 'Sem categoria'
    const previous = map.get(label)
    const value = parseFloat(item.valor)
    if (isNaN(value) || value <= 0) return

    map.set(label, {
      label,
      entrada: (previous?.entrada || 0) + (field === 'entrada' ? value : 0),
      saida: (previous?.saida || 0) + (field === 'saida' ? value : 0),
      total: (previous?.total || 0) + value,
      color:
        item.categoria_cor_hex ||
        previous?.color ||
        FALLBACK_COLORS[index % FALLBACK_COLORS.length],
    })
  }

  receitas.forEach((item, index) => addItem(item, index, 'entrada'))
  ;[...despesas, ...custos].forEach((item, index) =>
    addItem(item, index + receitas.length, 'saida'),
  )

  return Array.from(map.values()).sort((a, b) => b.total - a.total)
}
