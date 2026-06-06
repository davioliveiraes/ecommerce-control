import type { FinanceKpis } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface Props {
  kpis: FinanceKpis
}

const KPI_CONFIG = [
  {
    key: 'receita_total',
    label: 'Receitas',
    description: 'Entradas no período',
    tone: 'text-black',
  },
  {
    key: 'custo_total',
    label: 'Custos',
    description: 'Custos operacionais',
    tone: 'text-gray-700',
  },
  {
    key: 'despesa_total',
    label: 'Despesas',
    description: 'Saídas administrativas',
    tone: 'text-gray-700',
  },
  {
    key: 'lucro',
    label: 'Resultado',
    description: 'Receita menos saídas',
    tone: 'text-black',
  },
] as const

export function KpiCards({ kpis }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-px bg-gray-200 border border-gray-200">
      {KPI_CONFIG.map((item) => {
        const value = kpis[item.key]
        const numericValue = parseFloat(value)
        const tone =
          item.key === 'lucro'
            ? numericValue < 0
              ? 'text-gray-500'
              : 'text-black'
            : item.tone

        return (
          <div key={item.key} className="bg-white p-5">
            <div className="flex items-start justify-between gap-4 mb-5">
              <div>
                <div className="kicker mb-1">{item.label}</div>
                <p className="text-xs text-gray-600">{item.description}</p>
              </div>
              <SparkLineMark positive={item.key === 'receita_total'} />
            </div>
            <div
              className={`font-display text-2xl font-semibold tracking-tight tabular-nums ${tone}`}
            >
              {formatCurrency(value)}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function SparkLineMark({ positive }: { positive: boolean }) {
  return (
    <svg
      width="38"
      height="22"
      viewBox="0 0 38 22"
      fill="none"
      className={positive ? 'text-black' : 'text-gray-400'}
    >
      <path
        d="M1 17.5 9 10.5l7 4 8-11 13 7"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
