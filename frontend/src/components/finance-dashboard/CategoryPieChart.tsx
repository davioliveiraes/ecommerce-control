import { useState } from 'react'

import type { CategoriaFinanceira, FinanceFatiaCategoria } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface Props {
  receitas: FinanceFatiaCategoria[]
  despesas: FinanceFatiaCategoria[]
  custos: FinanceFatiaCategoria[]
  categorias: CategoriaFinanceira[]
  selectedCategoriaId: number | null
  onCategoriaChange: (categoriaId: number | null) => void
}

interface Slice {
  label: string
  entrada: number
  saida: number
  total: number
  color: string
}

const FALLBACK_COLORS = [
  '#1f4f8f',
  '#f97316',
  '#111827',
  '#737373',
  '#f59e0b',
  '#2563eb',
]

export function CategoryPieChart({
  receitas,
  despesas,
  custos,
  categorias,
  selectedCategoriaId,
  onCategoriaChange,
}: Props) {
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  const slices = buildSlices(receitas, despesas, custos)
  const totalEntradas = slices.reduce((acc, slice) => acc + slice.entrada, 0)
  const totalSaidas = slices.reduce((acc, slice) => acc + slice.saida, 0)
  const totalMovimentado = slices.reduce((acc, slice) => acc + slice.total, 0)
  const activeCategorias = categorias.filter((categoria) => categoria.ativo)
  const selectedCategoria = activeCategorias.find(
    (categoria) => categoria.id === selectedCategoriaId,
  )

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <div className="kicker mb-1">Categorias</div>
          <h2 className="font-display text-xl font-semibold text-black">
            Categorias financeiras
          </h2>
        </div>
        <div className="text-right font-mono text-xs text-gray-600 tabular-nums">
          <div>{formatCurrency(totalEntradas)} entradas</div>
          <div>{formatCurrency(totalSaidas)} saídas</div>
        </div>
      </div>

      <div className="relative mb-5">
        <button
          type="button"
          aria-haspopup="listbox"
          aria-expanded={isFilterOpen}
          onClick={() => setIsFilterOpen((open) => !open)}
          className="flex w-full items-center justify-between gap-3 border border-gray-200 bg-white px-3 py-2 text-left text-sm text-black hover:border-orange focus:outline-none focus:border-orange transition-colors"
        >
          <span className="min-w-0 truncate">
            {selectedCategoria ? selectedCategoria.nome : 'Todas as categorias'}
          </span>
          <IconChevronDown open={isFilterOpen} />
        </button>

        {isFilterOpen && (
          <div
            role="listbox"
            className="absolute left-0 right-0 top-[calc(100%+6px)] z-20 border border-gray-200 bg-white shadow-lg"
          >
            <CategoryOption
              label="Todas as categorias"
              active={selectedCategoriaId === null}
              onClick={() => {
                onCategoriaChange(null)
                setIsFilterOpen(false)
              }}
            />

            {activeCategorias.map((categoria) => (
              <CategoryOption
                key={categoria.id}
                label={categoria.nome}
                color={categoria.cor_hex}
                active={selectedCategoriaId === categoria.id}
                onClick={() => {
                  onCategoriaChange(categoria.id)
                  setIsFilterOpen(false)
                }}
              />
            ))}
          </div>
        )}
      </div>

      {slices.length === 0 ? (
        <div className="h-[300px] border border-dashed border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
          Sem categorias no período selecionado.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr] gap-6 items-center">
          <svg
            viewBox="0 0 220 220"
            role="img"
            aria-label="Distribuição financeira por categoria"
            className="w-full max-w-[260px] mx-auto"
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
                />
              )
            })}
            <circle cx="110" cy="110" r="48" fill="white" />
            <text
              x="110"
              y="105"
              textAnchor="middle"
              className="fill-gray-600"
              fontSize="11"
              fontFamily="monospace"
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
            >
              {slices.length}
            </text>
          </svg>

          <div className="space-y-2">
            {slices.map((slice) => (
              <div
                key={slice.label}
                className="grid grid-cols-[1fr_auto] gap-3 items-center border-b border-gray-100 pb-2 last:border-b-0"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className="h-2.5 w-2.5 shrink-0"
                      style={{ backgroundColor: slice.color }}
                    />
                    <span className="text-sm text-black truncate">
                      {slice.label}
                    </span>
                  </div>
                  <div className="mt-1 h-1.5 bg-gray-100">
                    <div
                      className="h-full"
                      style={{
                        width: `${(slice.total / totalMovimentado) * 100}%`,
                        backgroundColor: slice.color,
                      }}
                    />
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-xs text-navy tabular-nums">
                    + {formatCurrency(slice.entrada)}
                  </div>
                  <div className="font-mono text-xs text-orange-dark tabular-nums">
                    - {formatCurrency(slice.saida)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

function CategoryOption({
  label,
  color,
  active,
  onClick,
}: {
  label: string
  color?: string
  active: boolean
  onClick: () => void
}) {
  return (
    <button
      type="button"
      role="option"
      aria-selected={active}
      onClick={onClick}
      className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors ${
        active
          ? 'bg-orange-soft text-orange-dark'
          : 'text-gray-700 hover:bg-gray-50 hover:text-black'
      }`}
    >
      {color ? (
        <span
          className="h-2.5 w-2.5 shrink-0"
          style={{ backgroundColor: color }}
        />
      ) : (
        <span className="h-2.5 w-2.5 shrink-0 border border-gray-300 bg-white" />
      )}
      <span className="min-w-0 truncate">{label}</span>
    </button>
  )
}

function IconChevronDown({ open }: { open: boolean }) {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={`shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
    >
      <path d="m6 9 6 6 6-6" />
    </svg>
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
