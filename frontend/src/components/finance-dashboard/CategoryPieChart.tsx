import { useState } from 'react'
import type { FinanceFatiaCategoria } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface CategoryPieChartProps {
  receitas: FinanceFatiaCategoria[]
  despesas: FinanceFatiaCategoria[]
  custos: FinanceFatiaCategoria[]
}

interface Slice {
  label: string
  entrada: number
  saida: number
  total: number
  color: string
}

const FALLBACK_COLORS = [
  'var(--color-black)',
  'var(--color-gray-700)',
  'var(--color-gray-500)',
  'var(--color-gray-400)',
  'var(--color-gray-600)',
  'var(--color-gray-800)',
]

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
        <circle cx="110" cy="110" r="76" className="fill-gray-50" />
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
              strokeWidth="34"
              strokeDasharray={dashArray}
              strokeDashoffset={offset}
              pathLength="100"
              style={{ cursor: 'pointer', stroke: slice.color }}
              onMouseEnter={() => setHover({ slice, percentual })}
              onMouseLeave={() => setHover(null)}
            />
          )
        })}
        <circle
          cx="110"
          cy="110"
          r="48"
          className="fill-white"
          pointerEvents="none"
        />
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
