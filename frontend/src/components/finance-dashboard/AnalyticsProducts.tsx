import { useQuery } from '@tanstack/react-query'

import { fetchAnalyticsProdutos } from '../../api/analytics'
import type { ProdutoRanking } from '../../types/analytics'
import { DemoDataBanner } from './DemoDataBanner'

const NUVEMSHOP_PRODUCTS_ENDPOINTS = [
  {
    method: 'GET',
    path: '/2025-03/{store_id}/products?per_page=200',
    descricao:
      'Catálogo paginado (máx. 200/página): nome, marca, variantes, estoque.',
  },
  {
    method: 'GET',
    path: '/2025-03/{store_id}/products/{id}/variants',
    descricao:
      'Variantes com estoque atual por SKU — base do ranking de estoque crítico.',
  },
  {
    method: 'GET',
    path: '/2025-03/{store_id}/orders?payment_status=paid&fields=products',
    descricao:
      'Linhas de pedidos pagos → unidades vendidas e receita por SKU/variant.',
  },
  {
    method: 'GET',
    path: 'GA4 / Plausible (telemetria externa)',
    descricao:
      'Page views por produto — base do ranking de "mais visualizados".',
  },
]

export function AnalyticsProducts() {
  const query = useQuery({
    queryKey: ['analytics-produtos'],
    queryFn: fetchAnalyticsProdutos,
  })

  if (query.isLoading) {
    return (
      <div className="border border-gray-200 bg-white px-6 py-16 text-center font-mono text-sm text-gray-600">
        carregando produtos...
      </div>
    )
  }

  if (query.isError) {
    return (
      <div className="border border-gray-300 bg-gray-50 px-6 py-5">
        <div className="kicker mb-2">Erro</div>
        <h3 className="font-display text-lg font-semibold text-black mb-1">
          Falha ao carregar produtos
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
        source="API Nuvemshop (Produtos + Pedidos) + telemetria de page views"
        endpoints={NUVEMSHOP_PRODUCTS_ENDPOINTS}
      />

      <header>
        <div className="kicker mb-1">Estatísticas</div>
        <h2 className="font-display text-2xl font-semibold text-black">
          Produtos
        </h2>
        <p className="text-sm text-gray-600">
          Rankings dos produtos cadastrados — vendas, visualizações, estoque e
          margem.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <RankingPanel
          title="Mais vendidos"
          subtitle="Unidades vendidas no período · receita acumulada"
          items={data.mais_vendidos}
          metricLabel="vendas"
          emptyMessage="Sem vendas registradas no período."
        />
        <RankingPanel
          title="Mais visualizados"
          subtitle="Visualizações de produto · conversão em vendas"
          items={data.mais_visualizados}
          metricLabel="views"
          emptyMessage="Sem visualizações registradas."
        />
        <RankingPanel
          title="Estoque crítico"
          subtitle="Variações com 3 unidades ou menos disponíveis"
          items={data.estoque_critico}
          metricLabel=""
          emptyMessage="Nenhuma variação com estoque crítico."
          highlight="warn"
        />
        <RankingPanel
          title="Margem por produto"
          subtitle="Variações com maior margem percentual · receita estimada"
          items={data.margem_ranking}
          metricLabel="margem"
          emptyMessage="Sem variações para ranquear."
        />
      </div>
    </div>
  )
}

function RankingPanel({
  title,
  subtitle,
  items,
  metricLabel,
  emptyMessage,
  highlight,
}: {
  title: string
  subtitle: string
  items: ProdutoRanking[]
  metricLabel: string
  emptyMessage: string
  highlight?: 'warn'
}) {
  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="mb-4">
        <h3 className="font-display text-base font-semibold text-black">
          {title}
        </h3>
        <p className="mt-0.5 text-xs text-gray-600">{subtitle}</p>
      </div>

      {items.length === 0 ? (
        <div className="border border-dashed border-gray-200 bg-gray-50 px-4 py-8 text-center font-mono text-xs text-gray-500">
          {emptyMessage}
        </div>
      ) : (
        <ol className="space-y-2">
          {items.map((item, idx) => (
            <li
              key={`${item.sku}-${idx}`}
              className="grid grid-cols-[28px_minmax(0,1fr)_auto] items-center gap-3 border border-gray-100 px-3 py-2.5 hover:border-gray-300"
            >
              <span className="font-mono text-[11px] tabular-nums text-gray-500">
                {String(idx + 1).padStart(2, '0')}
              </span>
              <div className="min-w-0">
                <div className="truncate text-sm font-medium text-black" title={item.nome}>
                  {item.nome}
                </div>
                <div className="mt-0.5 flex items-center gap-2 font-mono text-[10px] uppercase tracking-wider text-gray-500">
                  <span className="truncate">{item.sku}</span>
                  <span className="text-gray-300">·</span>
                  <span className="truncate">{item.marca}</span>
                </div>
              </div>
              <div className="text-right">
                <div
                  className={`font-mono text-sm font-semibold tabular-nums ${
                    highlight === 'warn' ? 'text-black' : 'text-black'
                  }`}
                >
                  {item.valor_principal}
                  {metricLabel && (
                    <span className="ml-1 text-[10px] font-normal uppercase tracking-wider text-gray-500">
                      {metricLabel}
                    </span>
                  )}
                </div>
                {item.valor_secundario && (
                  <div className="font-mono text-[11px] text-gray-600">
                    {item.valor_secundario}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
