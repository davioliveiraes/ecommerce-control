import { useState } from 'react'
import type { FinanceMetricaReceitaVendas } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface BarHover {
  nome: string
  serie: 'Receita' | 'Vendas'
  valor: string
  color: string
  key: string
}

interface Props {
  formaPagamento: FinanceMetricaReceitaVendas[]
  meioPagamento: FinanceMetricaReceitaVendas[]
  parcelas: FinanceMetricaReceitaVendas[]
}

const MAIN_PAYMENT_METHODS = [
  { chave: 'PIX', nome: 'Pix' },
  { chave: 'CARTAO_CREDITO', nome: 'Cartão de crédito' },
]

export function PaymentStatisticsPanel({
  formaPagamento,
  meioPagamento,
  parcelas,
}: Props) {
  const formas = normalizePaymentMethods(formaPagamento)
  const hasData = formas.some((item) => parseFloat(item.receita) > 0 || item.vendas > 0)
  const totalReceita = sumReceita(formaPagamento)
  const totalVendas = sumVendas(formaPagamento)
  const summaryCards = [
    {
      color: '#0a0a0a',
      title: 'Receita por forma de pagamento',
      value: formatCurrency(sumReceita(formaPagamento)),
      details: buildDetails(formas, 'receita'),
    },
    {
      color: '#404040',
      title: 'Vendas por forma de pagamento',
      value: sumVendas(formaPagamento).toLocaleString('pt-BR'),
      details: buildDetails(formas, 'vendas'),
    },
    {
      color: '#525252',
      title: 'Receita por meio de pagamento',
      value: formatCurrency(sumReceita(meioPagamento)),
      details: buildDetails(meioPagamento, 'receita'),
    },
    {
      color: '#737373',
      title: 'Vendas por meio de pagamento',
      value: sumVendas(meioPagamento).toLocaleString('pt-BR'),
      details: buildDetails(meioPagamento, 'vendas'),
    },
    {
      color: '#262626',
      title: 'Receita por quantidade de parcelas',
      value: formatCurrency(sumReceita(parcelas)),
      details: buildDetails(parcelas, 'receita'),
    },
    {
      color: '#a3a3a3',
      title: 'Vendas por quantidade de parcelas',
      value: sumVendas(parcelas).toLocaleString('pt-BR'),
      details: buildDetails(parcelas, 'vendas'),
    },
  ]

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
          <Legend color="#0a0a0a" label="Receita" />
          <Legend color="#a3a3a3" label="Vendas" />
        </div>
      </div>

      {!hasData ? (
        <div className="h-[320px] border border-dashed border-gray-200 bg-gray-50 flex items-center justify-center text-sm text-gray-600">
          Sem estatísticas de pagamento no período selecionado.
        </div>
      ) : (
        <>
          <div className="mb-4">
            <h3 className="font-display text-lg font-semibold text-black">
              Seus pagamentos: visão geral
            </h3>
            <p className="text-xs text-gray-600 mt-1">
              Comparativo consolidado entre receita e volume de vendas.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)_420px] xl:gap-5">
            <OverviewCard
              label="Receita em pagamentos"
              value={formatCurrency(totalReceita)}
            />
            <OverviewCard
              label="Vendas pagas"
              value={totalVendas.toLocaleString('pt-BR')}
            />
            <SummaryCard {...summaryCards[0]} />

            <div className="xl:col-span-2 h-full">
              <PaymentOverviewChart data={formas} />
            </div>

            <div className="space-y-3">
              {summaryCards.slice(1).map((card) => (
                <SummaryCard key={card.title} {...card} />
              ))}
            </div>
          </div>
        </>
      )}
    </section>
  )
}

function PaymentOverviewChart({
  data,
}: {
  data: FinanceMetricaReceitaVendas[]
}) {
  const [hover, setHover] = useState<BarHover | null>(null)
  const maxReceita = Math.max(1, ...data.map((item) => parseFloat(item.receita)))
  const maxVendas = Math.max(1, ...data.map((item) => item.vendas))
  const maxChartValue = Math.max(maxReceita, maxVendas)

  return (
    <div
      role="img"
      aria-label="Receita e vendas por forma de pagamento"
      className="relative h-full min-h-[430px] border border-gray-200 px-5 pt-6 pb-4"
    >
      <div
        className="grid h-[calc(100%-2.25rem)] min-h-[360px] items-end gap-8 border-b border-gray-300"
        style={{
          gridTemplateColumns: `repeat(${data.length}, minmax(120px, 1fr))`,
        }}
      >
        {data.map((item) => {
          const receita = parseFloat(item.receita)
          const receitaHeight = (receita / maxChartValue) * 100
          const vendasHeight = (item.vendas / maxChartValue) * 100

          return (
            <div
              key={item.chave}
              className="flex h-full min-w-0 flex-col"
            >
              <div className="mb-2 grid grid-cols-2 gap-2 text-center font-mono text-[11px] text-gray-600">
                <span>{formatCurrency(receita)}</span>
                <span>{item.vendas.toLocaleString('pt-BR')}</span>
              </div>

              <div className="flex min-h-0 flex-1 items-end justify-center gap-3">
                <Bar
                  color="#0a0a0a"
                  height={receitaHeight}
                  onEnter={() =>
                    setHover({
                      key: `${item.chave}-r`,
                      nome: item.nome,
                      serie: 'Receita',
                      valor: formatCurrency(receita),
                      color: '#0a0a0a',
                    })
                  }
                  onLeave={() => setHover(null)}
                />
                <Bar
                  color="#a3a3a3"
                  height={vendasHeight}
                  onEnter={() =>
                    setHover({
                      key: `${item.chave}-v`,
                      nome: item.nome,
                      serie: 'Vendas',
                      valor: item.vendas.toLocaleString('pt-BR'),
                      color: '#a3a3a3',
                    })
                  }
                  onLeave={() => setHover(null)}
                />
              </div>

              <div className="mt-3 truncate text-center font-mono text-sm text-gray-600">
                {shortLabel(item.nome)}
              </div>
            </div>
          )
        })}
      </div>

      {hover && (
        <div className="pointer-events-none absolute left-1/2 top-3 z-10 -translate-x-1/2 border border-black bg-white px-3 py-2 shadow-lg min-w-[180px]">
          <div className="flex items-center gap-2 text-[11px] font-medium uppercase tracking-wider text-gray-600">
            <span className="h-2 w-2" style={{ backgroundColor: hover.color }} />
            {hover.nome} · {hover.serie}
          </div>
          <div className="mt-1 font-mono text-sm font-semibold tabular-nums text-black">
            {hover.valor}
          </div>
        </div>
      )}
    </div>
  )
}

function OverviewCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-gray-200 bg-gray-50 px-4 py-3">
      <div className="font-mono text-[10px] uppercase tracking-wider text-gray-600 mb-1">
        {label}
      </div>
      <div className="font-mono text-lg text-black tabular-nums">{value}</div>
    </div>
  )
}

function Bar({
  color,
  height,
  onEnter,
  onLeave,
}: {
  color: string
  height: number
  onEnter: () => void
  onLeave: () => void
}) {
  return (
    <div className="flex h-full flex-col items-center justify-end gap-1">
      <div
        onMouseEnter={onEnter}
        onMouseLeave={onLeave}
        className="w-20 cursor-pointer transition-[height] duration-300"
        style={{
          height: `${Math.max(1, height)}%`,
          backgroundColor: color,
        }}
      />
    </div>
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

function shortLabel(label: string) {
  if (label === 'Cartão de crédito') return 'Cartão'
  return label
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

function normalizePaymentMethods(data: FinanceMetricaReceitaVendas[]) {
  const mapped = new Map(data.map((item) => [item.chave, item]))
  const preferred = MAIN_PAYMENT_METHODS.map((method) => {
    return (
      mapped.get(method.chave) || {
        chave: method.chave,
        nome: method.nome,
        receita: '0',
        vendas: 0,
      }
    )
  })

  const extra = data.filter(
    (item) => !MAIN_PAYMENT_METHODS.some((method) => method.chave === item.chave),
  )

  return [...preferred, ...extra]
}
