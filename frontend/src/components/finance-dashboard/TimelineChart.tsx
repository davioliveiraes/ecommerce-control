import { useState } from 'react'
import type { FinancePontoMensal, TipoLancamento } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface Props {
  data: FinancePontoMensal[]
  visibleTypes?: TipoLancamento[]
}

interface HoverState {
  serieLabel: string
  mes: string
  value: number
  color: string
  x: number
  y: number
}

// viewBox achatado (aspecto largo) para o gráfico preencher o container sem
// ficar alto demais quando ocupa a largura toda.
const WIDTH = 1000
const HEIGHT = 224
const PADDING_X = 44
const PADDING_Y = 32

const SERIES = [
  { key: 'receita', label: 'Receita', color: 'var(--color-black)' },
  { key: 'custo', label: 'Custo', color: 'var(--color-gray-500)' },
  { key: 'despesa', label: 'Despesa', color: 'var(--color-gray-400)' },
] as const

const TYPE_TO_SERIES_KEY: Record<TipoLancamento, (typeof SERIES)[number]['key']> = {
  RECEITA: 'receita',
  CUSTO: 'custo',
  DESPESA: 'despesa',
}

export function TimelineChart({ data, visibleTypes }: Props) {
  const [hover, setHover] = useState<HoverState | null>(null)
  const visibleKeys = visibleTypes?.map((tipo) => TYPE_TO_SERIES_KEY[tipo])
  const activeSeries = visibleKeys
    ? SERIES.filter((serie) => visibleKeys.includes(serie.key))
    : SERIES

  const parsed = data.map((point) => ({
    mes: point.mes,
    receita: parseFloat(point.receita),
    custo: parseFloat(point.custo),
    despesa: parseFloat(point.despesa),
  }))

  const maxValue = Math.max(
    1,
    ...parsed.flatMap((point) => activeSeries.map((serie) => point[serie.key])),
  )
  const chartWidth = WIDTH - PADDING_X * 2
  const chartHeight = HEIGHT - PADDING_Y * 2

  const xFor = (index: number) => {
    if (parsed.length <= 1) return PADDING_X + chartWidth / 2
    return PADDING_X + (index / (parsed.length - 1)) * chartWidth
  }
  const yFor = (value: number) => {
    return PADDING_Y + chartHeight - (value / maxValue) * chartHeight
  }

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="kicker mb-1">Linha temporal</div>
          <h2 className="font-display text-xl font-semibold text-black">
            Evolução mensal
          </h2>
        </div>
        <div className="flex flex-wrap justify-end gap-3">
          {activeSeries.map((serie) => (
            <span
              key={serie.key}
              className="inline-flex items-center gap-1.5 text-xs text-gray-600"
            >
              <span
                className="h-2 w-2"
                style={{ backgroundColor: serie.color }}
              />
              {serie.label}
            </span>
          ))}
        </div>
      </div>

      {parsed.length === 0 ? (
        <EmptyChartState message="Sem dados no período selecionado." />
      ) : (
        <div className="relative w-full">
          <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            role="img"
            aria-label="Evolução mensal financeira"
            className="w-full h-auto"
          >
            {[0, 0.25, 0.5, 0.75, 1].map((step) => {
              const y = PADDING_Y + chartHeight - step * chartHeight
              return (
                <g key={step}>
                  <line
                    x1={PADDING_X}
                    x2={WIDTH - PADDING_X}
                    y1={y}
                    y2={y}
                    className="stroke-gray-200"
                    strokeWidth="1"
                  />
                  <text
                    x={PADDING_X}
                    y={y - 6}
                    className="fill-gray-500"
                    fontSize="9"
                    fontFamily="monospace"
                  >
                    {formatCurrency(maxValue * step)}
                  </text>
                </g>
              )
            })}

            {activeSeries.map((serie) => {
              const d = parsed
                .map((point, index) => {
                  const value = point[serie.key]
                  const command = index === 0 ? 'M' : 'L'
                  return `${command} ${xFor(index)} ${yFor(value)}`
                })
                .join(' ')

              return (
                <g key={serie.key}>
                  <path
                    d={d}
                    fill="none"
                    style={{ stroke: serie.color }}
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  {parsed.map((point, index) => (
                    <g key={`${serie.key}-${point.mes}`}>
                      <circle
                        cx={xFor(index)}
                        cy={yFor(point[serie.key])}
                        r="3.5"
                        className="fill-white"
                        style={{ stroke: serie.color }}
                        strokeWidth="2"
                      />
                      <circle
                        cx={xFor(index)}
                        cy={yFor(point[serie.key])}
                        r="12"
                        fill="transparent"
                        style={{ cursor: 'pointer' }}
                        onMouseEnter={(event) => {
                          const svg = event.currentTarget.ownerSVGElement
                          if (!svg) return
                          const rect = svg.getBoundingClientRect()
                          const scaleX = rect.width / WIDTH
                          const scaleY = rect.height / HEIGHT
                          setHover({
                            serieLabel: serie.label,
                            mes: point.mes,
                            value: point[serie.key],
                            color: serie.color,
                            x: xFor(index) * scaleX,
                            y: yFor(point[serie.key]) * scaleY,
                          })
                        }}
                        onMouseLeave={() => setHover(null)}
                      />
                    </g>
                  ))}
                </g>
              )
            })}

            {parsed.map((point, index) => (
              <text
                key={point.mes}
                x={xFor(index)}
                y={HEIGHT - 8}
                className="fill-gray-500"
                fontSize="10"
                fontFamily="monospace"
                textAnchor="middle"
              >
                {formatMonth(point.mes)}
              </text>
            ))}
          </svg>

          {hover && (() => {
            const flipBelow = hover.y < 70
            const verticalClass = flipBelow ? '' : '-translate-y-full'
            const top = flipBelow ? hover.y + 18 : hover.y - 18
            return (
              <div
                className={`pointer-events-none absolute z-10 -translate-x-1/2 border border-black bg-white px-3 py-2 shadow-lg ${verticalClass}`}
                style={{ left: hover.x, top }}
              >
                <div className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-wider text-gray-600">
                  <span
                    className="h-2 w-2"
                    style={{ backgroundColor: hover.color }}
                  />
                  {hover.serieLabel} · {formatMonth(hover.mes)}
                </div>
                <div className="mt-1 font-mono text-sm font-semibold tabular-nums text-black">
                  {formatCurrency(hover.value)}
                </div>
              </div>
            )
          })()}
        </div>
      )}
    </section>
  )
}

function EmptyChartState({ message }: { message: string }) {
  return (
    <div className="h-[300px] border border-dashed border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
      {message}
    </div>
  )
}

function formatMonth(value: string) {
  const [year, month] = value.split('-')
  if (!year || !month) return value
  return `${month}/${year.slice(2)}`
}
