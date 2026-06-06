import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'

import { fetchAnalyticsOverview } from '../../api/analytics'
import type {
  BehaviorItem,
  ConversionItem,
  KpiSerie,
} from '../../types/analytics'
import { formatCurrency, formatPercent } from '../../utils/format'
import { DemoDataBanner } from './DemoDataBanner'
import { MiniSparkline } from './MiniSparkline'

const NUVEMSHOP_OVERVIEW_ENDPOINTS = [
  {
    method: 'GET',
    path: '/v1/{store_id}/orders?paid_status=paid&created_at_min=...',
    descricao: 'Pedidos pagos no período → vendas, receita, ticket médio.',
  },
  {
    method: 'GET',
    path: '/v1/{store_id}/orders?status=open',
    descricao: 'Carrinhos abandonados → checkouts iniciados sem conversão.',
  },
  {
    method: 'GET',
    path: 'Analytics API (beta) ou GA4 / Plausible',
    descricao: 'Visitas, visualizações de categoria e produto (telemetria externa).',
  },
]

export function AnalyticsOverview() {
  const query = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: fetchAnalyticsOverview,
  })

  if (query.isLoading) {
    return (
      <div className="border border-gray-200 bg-white px-6 py-16 text-center font-mono text-sm text-gray-600">
        carregando visão geral...
      </div>
    )
  }

  if (query.isError) {
    return (
      <div className="border border-gray-300 bg-gray-50 px-6 py-5">
        <div className="kicker mb-2">Erro</div>
        <h3 className="font-display text-lg font-semibold text-black mb-1">
          Falha ao carregar a visão geral
        </h3>
        <p className="text-sm text-gray-600">
          {(query.error as Error)?.message || 'Erro desconhecido'}
        </p>
      </div>
    )
  }

  if (!query.data) return null

  const data = query.data

  return (
    <div className="space-y-5">
      <DemoDataBanner
        source="API Nuvemshop (Pedidos + Analytics) + telemetria de visitas"
        endpoints={NUVEMSHOP_OVERVIEW_ENDPOINTS}
      />

      <header className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="kicker mb-1">Estatísticas</div>
          <h2 className="font-display text-2xl font-semibold text-black">
            Visão geral
          </h2>
          <p className="text-sm text-gray-600">
            Exibindo dados de acordo com a{' '}
            <strong className="text-black">data de criação</strong> do pedido.
          </p>
        </div>
        <div className="flex items-center gap-2 font-mono text-xs text-gray-600">
          <IconClock />
          Última atualização: {formatUpdate(data.ultima_atualizacao)}
        </div>
      </header>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <KpiSparkCard
          label="Visitas"
          info="Total de visitas únicas no período."
          serie={data.kpis.visitas}
          color="#0a0a0a"
        />
        <KpiSparkCard
          label="Vendas"
          info="Total de pedidos pagos no período."
          serie={data.kpis.vendas}
          color="#404040"
        />
        <KpiSparkCard
          label="Receita"
          info="Receita bruta dos pedidos pagos."
          serie={data.kpis.receita}
          color="#262626"
        />
        <KpiSparkCard
          label="Ticket médio"
          info="Receita dividida pelo total de vendas."
          serie={data.kpis.ticket_medio}
          color="#737373"
        />
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1fr)_360px]">
        <div className="space-y-3">
          <BehaviorPanel
            title="Comportamento dos visitantes"
            info="Funil de navegação dos visitantes na loja."
            items={data.comportamento_visitantes}
          />
          <BehaviorPanel
            title="Comportamento no checkout"
            info="Conversão entre etapas do checkout."
            items={data.comportamento_checkout}
          />
        </div>

        <div className="space-y-3">
          {data.conversoes.map((conv) => (
            <ConversionCard key={conv.label} item={conv} />
          ))}
        </div>
      </div>
    </div>
  )
}

function KpiSparkCard({
  label,
  info,
  serie,
  color,
}: {
  label: string
  info: string
  serie: KpiSerie
  color: string
}) {
  const valor =
    typeof serie.valor === 'string' ? parseFloat(serie.valor) || 0 : serie.valor

  const display =
    serie.formato === 'moeda'
      ? formatCurrency(valor)
      : valor.toLocaleString('pt-BR')

  return (
    <div className="border border-gray-200 bg-white px-4 py-4">
      <div className="mb-2 flex items-center gap-1.5">
        <span className="text-sm font-medium text-black">{label}</span>
        <InfoTip text={info} />
      </div>
      <div className="font-mono text-2xl font-semibold tabular-nums text-black">
        {display}
      </div>
      <div className="mt-3">
        <MiniSparkline
          serie={serie.serie}
          labels={serie.labels}
          formato={serie.formato}
          color={color}
        />
      </div>
    </div>
  )
}

function BehaviorPanel({
  title,
  info,
  items,
}: {
  title: string
  info: string
  items: BehaviorItem[]
}) {
  const max = Math.max(1, ...items.map((item) => item.valor))

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="mb-4 flex items-center gap-1.5">
        <h3 className="font-display text-base font-semibold text-black">
          {title}
        </h3>
        <InfoTip text={info} />
      </div>

      <div className="space-y-2.5">
        {items.map((item, idx) => (
          <HorizontalBar
            key={item.label}
            label={item.label}
            value={item.valor}
            max={max}
            color={shadeFor(idx, items.length)}
          />
        ))}
      </div>
    </section>
  )
}

function HorizontalBar({
  label,
  value,
  max,
  color,
}: {
  label: string
  value: number
  max: number
  color: string
}) {
  const [isHover, setIsHover] = useState(false)
  const width = (value / max) * 100

  return (
    <div className="grid grid-cols-[140px_minmax(0,1fr)_64px] items-center gap-3 text-xs">
      <span
        className="truncate font-mono text-gray-600"
        title={label}
      >
        {label}
      </span>
      <div className="relative h-6 bg-gray-50">
        <div
          onMouseEnter={() => setIsHover(true)}
          onMouseLeave={() => setIsHover(false)}
          className="h-full cursor-pointer transition-[width] duration-300"
          style={{ width: `${Math.max(0.4, width)}%`, backgroundColor: color }}
        />
        {isHover && (
          <div
            className="pointer-events-none absolute z-10 -translate-y-full border border-black bg-white px-2 py-1 shadow-md"
            style={{ left: `min(${width}%, calc(100% - 130px))`, top: -4 }}
          >
            <div className="font-mono text-[10px] uppercase tracking-wider text-gray-600">
              {label}
            </div>
            <div className="font-mono text-xs font-semibold tabular-nums text-black">
              {value.toLocaleString('pt-BR')}
            </div>
          </div>
        )}
      </div>
      <span className="text-right font-mono tabular-nums text-black">
        {value.toLocaleString('pt-BR')}
      </span>
    </div>
  )
}

function ConversionCard({ item }: { item: ConversionItem }) {
  return (
    <div className="border border-gray-200 bg-white px-4 py-4">
      <div className="mb-1 flex items-center gap-1.5">
        <span className="text-sm font-medium text-black">{item.label}</span>
        <InfoTip text={item.detalhe || ''} />
      </div>
      <div className="font-mono text-xs uppercase tracking-wider text-gray-500">
        Conversão
      </div>
      <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-black">
        {formatPercent(item.valor_percentual)}
      </div>
      {item.detalhe && (
        <p className="mt-2 text-xs text-gray-600">{item.detalhe}</p>
      )}
      <div className="mt-3 h-1 bg-gray-100">
        <div
          className="h-1 bg-black"
          style={{ width: `${Math.min(100, item.valor_percentual)}%` }}
        />
      </div>
    </div>
  )
}

function InfoTip({ text }: { text: string }) {
  if (!text) return null
  return (
    <span
      title={text}
      className="inline-flex h-3.5 w-3.5 cursor-help items-center justify-center rounded-full border border-gray-300 text-[9px] font-bold text-gray-500"
    >
      i
    </span>
  )
}

function IconClock() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  )
}

function shadeFor(index: number, total: number) {
  const shades = ['#0a0a0a', '#262626', '#404040', '#525252', '#737373', '#a3a3a3']
  if (total <= shades.length) return shades[index] || shades[shades.length - 1]
  return shades[index % shades.length]
}

function formatUpdate(iso: string) {
  try {
    const date = new Date(iso)
    return `${date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
    })} · ${date.toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
    })}`
  } catch {
    return iso
  }
}
