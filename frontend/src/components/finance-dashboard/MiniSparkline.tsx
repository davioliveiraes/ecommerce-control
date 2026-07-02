import { useState } from 'react'
import { formatCurrency } from '../../utils/format'

export type SparkFormato = 'inteiro' | 'moeda'

interface Props {
  serie: Array<number | string>
  labels: string[]
  formato: SparkFormato
  color?: string
  height?: number
}

interface Hover {
  x: number
  y: number
  label: string
  value: number
}

const WIDTH = 280
const PADDING_X = 6
const PADDING_Y = 8

export function MiniSparkline({
  serie,
  labels,
  formato,
  color = 'var(--color-black)',
  height = 60,
}: Props) {
  const [hover, setHover] = useState<Hover | null>(null)

  const points = serie.map((v) =>
    typeof v === 'string' ? parseFloat(v) || 0 : v,
  )

  if (points.length === 0) {
    return (
      <div
        className="flex items-center justify-center font-mono text-[10px] text-gray-400"
        style={{ height }}
      >
        sem dados
      </div>
    )
  }

  const max = Math.max(...points, 1)
  const min = Math.min(...points, 0)
  const range = Math.max(max - min, 1)
  const chartW = WIDTH - PADDING_X * 2
  const chartH = height - PADDING_Y * 2

  const xFor = (i: number) =>
    points.length === 1
      ? PADDING_X + chartW / 2
      : PADDING_X + (i / (points.length - 1)) * chartW
  const yFor = (v: number) =>
    PADDING_Y + chartH - ((v - min) / range) * chartH

  const linePath = points
    .map((v, i) => `${i === 0 ? 'M' : 'L'} ${xFor(i)} ${yFor(v)}`)
    .join(' ')

  const areaPath = `${linePath} L ${xFor(points.length - 1)} ${
    height - PADDING_Y
  } L ${xFor(0)} ${height - PADDING_Y} Z`

  const formatValue = (v: number) =>
    formato === 'moeda' ? formatCurrency(v) : v.toLocaleString('pt-BR')

  return (
    <div className="relative w-full">
      <svg
        viewBox={`0 0 ${WIDTH} ${height}`}
        preserveAspectRatio="none"
        className="block w-full"
        style={{ height }}
      >
        <path d={areaPath} style={{ fill: color }} opacity={0.06} />
        <path
          d={linePath}
          fill="none"
          style={{ stroke: color }}
          strokeWidth={1.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          vectorEffect="non-scaling-stroke"
        />
        {points.map((v, i) => {
          const cx = xFor(i)
          const cy = yFor(v)
          return (
            <g key={i}>
              <circle cx={cx} cy={cy} r={1.6} style={{ fill: color }} />
              <circle
                cx={cx}
                cy={cy}
                r={10}
                fill="transparent"
                style={{ cursor: 'pointer' }}
                onMouseEnter={(e) => {
                  const svg = e.currentTarget.ownerSVGElement
                  if (!svg) return
                  const rect = svg.getBoundingClientRect()
                  setHover({
                    x: (cx / WIDTH) * rect.width,
                    y: (cy / height) * rect.height,
                    label: labels[i] || '',
                    value: v,
                  })
                }}
                onMouseLeave={() => setHover(null)}
              />
            </g>
          )
        })}
      </svg>

      {hover && (
        <div
          className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full whitespace-nowrap border border-black bg-white px-2 py-1 shadow-md"
          style={{ left: hover.x, top: hover.y - 8 }}
        >
          <div className="flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-wider text-gray-600">
            <span
              className="inline-block h-1.5 w-1.5"
              style={{ backgroundColor: color }}
            />
            {hover.label}
          </div>
          <div className="font-mono text-xs font-semibold tabular-nums text-black">
            {formatValue(hover.value)}
          </div>
        </div>
      )}
    </div>
  )
}
