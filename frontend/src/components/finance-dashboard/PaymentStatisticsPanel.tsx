import type { FinanceMetricaReceitaVendas } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface Props {
  formaPagamento: FinanceMetricaReceitaVendas[]
  meioPagamento: FinanceMetricaReceitaVendas[]
  parcelas: FinanceMetricaReceitaVendas[]
}

interface Group {
  label: string
  data: FinanceMetricaReceitaVendas[]
  colorReceita: string
  colorVendas: string
}

const WIDTH = 720
const HEIGHT = 330
const PADDING = 46

export function PaymentStatisticsPanel({
  formaPagamento,
  meioPagamento,
  parcelas,
}: Props) {
  const groups: Group[] = [
    {
      label: 'Forma',
      data: formaPagamento,
      colorReceita: '#0ea5b7',
      colorVendas: '#d6008f',
    },
    {
      label: 'Meio',
      data: meioPagamento,
      colorReceita: '#9b35a7',
      colorVendas: '#1d1ee8',
    },
    {
      label: 'Parcelas',
      data: parcelas,
      colorReceita: '#f59e0b',
      colorVendas: '#c2412d',
    },
  ]

  const hasData = groups.some((group) => group.data.length > 0)
  const totalReceita = groups.reduce(
    (acc, group) => acc + sumReceita(group.data),
    0,
  )
  const totalVendas = groups.reduce((acc, group) => acc + sumVendas(group.data), 0)

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <div className="kicker mb-1">Pagamentos</div>
          <h2 className="font-display text-xl font-semibold text-black">
            Estatísticas de pagamento
          </h2>
        </div>
        <div className="hidden sm:flex gap-3 text-xs text-gray-600">
          <Legend color="#9bbfed" label="Receita" />
          <Legend color="#c9ddf8" label="Vendas" />
        </div>
      </div>

      {!hasData ? (
        <div className="h-[320px] border border-dashed border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
          Sem estatísticas de pagamento no período selecionado.
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_420px] gap-5">
          <div className="min-w-0">
            <div className="mb-4">
              <h3 className="font-display text-lg font-semibold text-black">
                Seus pagamentos: visão geral
              </h3>
              <p className="text-xs text-gray-600 mt-1">
                Comparativo consolidado entre receita e volume de vendas.
              </p>
            </div>

            <PaymentOverviewChart groups={groups} />
          </div>

          <div className="space-y-3">
            <SummaryCard
              color="#0ea5b7"
              title="Receita por forma de pagamento"
              value={formatCurrency(sumReceita(formaPagamento))}
              details={buildDetails(formaPagamento, 'receita')}
            />
            <SummaryCard
              color="#d6008f"
              title="Vendas por forma de pagamento"
              value={sumVendas(formaPagamento).toLocaleString('pt-BR')}
              details={buildDetails(formaPagamento, 'vendas')}
            />
            <SummaryCard
              color="#9b35a7"
              title="Receita por meio de pagamento"
              value={formatCurrency(sumReceita(meioPagamento))}
              details={buildDetails(meioPagamento, 'receita')}
            />
            <SummaryCard
              color="#1d1ee8"
              title="Vendas por meio de pagamento"
              value={sumVendas(meioPagamento).toLocaleString('pt-BR')}
              details={buildDetails(meioPagamento, 'vendas')}
            />
            <SummaryCard
              color="#f59e0b"
              title="Receita por quantidade de parcelas"
              value={formatCurrency(sumReceita(parcelas))}
              details={buildDetails(parcelas, 'receita')}
            />
            <SummaryCard
              color="#c2412d"
              title="Vendas por quantidade de parcelas"
              value={sumVendas(parcelas).toLocaleString('pt-BR')}
              details={buildDetails(parcelas, 'vendas')}
            />

            <div className="border border-gray-200 bg-gray-50 px-4 py-3">
              <div className="grid grid-cols-2 gap-3">
                <Metric label="Receita analisada" value={formatCurrency(totalReceita)} />
                <Metric
                  label="Vendas analisadas"
                  value={totalVendas.toLocaleString('pt-BR')}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}

function PaymentOverviewChart({ groups }: { groups: Group[] }) {
  const chartWidth = WIDTH - PADDING * 2
  const chartHeight = HEIGHT - PADDING * 2
  const maxReceita = Math.max(1, ...groups.map((group) => sumReceita(group.data)))
  const maxVendas = Math.max(1, ...groups.map((group) => sumVendas(group.data)))
  const barWidth = 54

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      role="img"
      aria-label="Receita e vendas por estatísticas de pagamento"
      className="w-full h-auto"
    >
      {[0, 0.25, 0.5, 0.75, 1].map((step) => {
        const y = PADDING + chartHeight - step * chartHeight
        return (
          <line
            key={step}
            x1={PADDING}
            x2={WIDTH - PADDING}
            y1={y}
            y2={y}
            stroke="#e5e5e5"
            strokeWidth="1"
          />
        )
      })}

      {groups.map((group, index) => {
        const groupWidth = chartWidth / groups.length
        const center = PADDING + groupWidth * index + groupWidth / 2
        const receitaHeight = (sumReceita(group.data) / maxReceita) * chartHeight
        const vendasHeight = (sumVendas(group.data) / maxVendas) * chartHeight

        return (
          <g key={group.label}>
            <rect
              x={center - barWidth - 5}
              y={PADDING + chartHeight - receitaHeight}
              width={barWidth}
              height={receitaHeight}
              fill="#9bbfed"
            />
            <rect
              x={center + 5}
              y={PADDING + chartHeight - vendasHeight}
              width={barWidth}
              height={vendasHeight}
              fill="#c9ddf8"
            />
            <text
              x={center}
              y={HEIGHT - 14}
              textAnchor="middle"
              fill="#737373"
              fontSize="12"
              fontFamily="monospace"
            >
              {group.label}
            </text>
          </g>
        )
      })}

      <line
        x1={PADDING}
        x2={WIDTH - PADDING}
        y1={PADDING + chartHeight}
        y2={PADDING + chartHeight}
        stroke="#d4d4d4"
      />
    </svg>
  )
}

function SummaryCard({
  color,
  title,
  value,
  details,
}: {
  color: string
  title: string
  value: string
  details: string
}) {
  return (
    <div className="border border-gray-200 px-4 py-3">
      <div className="flex items-center gap-2 mb-3">
        <span className="h-3 w-3" style={{ backgroundColor: color }} />
        <span className="text-sm font-medium text-black">{title}</span>
      </div>
      <div className="font-mono text-sm text-black tabular-nums">{value}</div>
      {details && (
        <div className="mt-2 font-mono text-[11px] text-gray-600 truncate">
          {details}
        </div>
      )}
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="font-mono text-[10px] uppercase tracking-wider text-gray-600 mb-1">
        {label}
      </div>
      <div className="font-mono text-sm text-black tabular-nums">{value}</div>
    </div>
  )
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className="h-2.5 w-2.5" style={{ backgroundColor: color }} />
      {label}
    </span>
  )
}

function sumReceita(data: FinanceMetricaReceitaVendas[]) {
  return data.reduce((acc, item) => acc + parseFloat(item.receita), 0)
}

function sumVendas(data: FinanceMetricaReceitaVendas[]) {
  return data.reduce((acc, item) => acc + item.vendas, 0)
}

function buildDetails(
  data: FinanceMetricaReceitaVendas[],
  mode: 'receita' | 'vendas',
) {
  return data
    .slice(0, 3)
    .map((item) => {
      const value =
        mode === 'receita'
          ? formatCurrency(item.receita)
          : item.vendas.toLocaleString('pt-BR')
      return `${item.nome}: ${value}`
    })
    .join(' · ')
}
