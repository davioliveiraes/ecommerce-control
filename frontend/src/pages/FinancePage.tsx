import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchCategoriasFinanceiras } from '../api/categoriasFinanceiras'
import { fetchFinanceDashboard } from '../api/financeDashboard'
import { CategoryPieChart } from '../components/finance-dashboard/CategoryPieChart'
import { DashboardFilters } from '../components/finance-dashboard/DashboardFilters'
import { KpiCards } from '../components/finance-dashboard/KpiCards'
import { PaymentStatisticsPanel } from '../components/finance-dashboard/PaymentStatisticsPanel'
import { TimelineChart } from '../components/finance-dashboard/TimelineChart'

export function FinancePage() {
  const [dataInicio, setDataInicio] = useState(getStartOfCurrentYear())
  const [dataFim, setDataFim] = useState(getTodayInputValue())
  const [incluirPendentes, setIncluirPendentes] = useState(false)
  const [categoriaId, setCategoriaId] = useState<number | null>(null)

  const dashboardQuery = useQuery({
    queryKey: [
      'finance-dashboard',
      { dataInicio, dataFim, incluirPendentes, categoriaId },
    ],
    queryFn: () =>
      fetchFinanceDashboard({
        data_inicio: dataInicio,
        data_fim: dataFim,
        categoria_id: categoriaId,
        incluir_pendentes: incluirPendentes,
      }),
  })

  const categoriasQuery = useQuery({
    queryKey: ['categorias-financeiras'],
    queryFn: fetchCategoriasFinanceiras,
  })

  const clearFilters = () => {
    setDataInicio('')
    setDataFim('')
    setCategoriaId(null)
    setIncluirPendentes(false)
  }

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <div className="flex items-start justify-between gap-6 mb-5">
        <div className="min-w-0">
          <div className="kicker mb-1.5">Módulo 02</div>
          <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
            Dashboard Financeiro
          </h1>
            <p className="text-sm text-gray-600 mt-1 max-w-3xl">
              Resultado consolidado dos lançamentos financeiros, com visão mensal
              e estatísticas de categorias e pagamentos.
            </p>
        </div>

        <Link
          to="/finance/lancamentos"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-orange bg-orange text-white hover:bg-orange-dark hover:border-orange-dark transition-colors shrink-0"
        >
          <IconList />
          Lançamentos
        </Link>
      </div>

      <div className="space-y-5">
        <DashboardFilters
          dataInicio={dataInicio}
          dataFim={dataFim}
          incluirPendentes={incluirPendentes}
          onDataInicioChange={setDataInicio}
          onDataFimChange={setDataFim}
          onIncluirPendentesChange={setIncluirPendentes}
          onClear={clearFilters}
        />

        {dashboardQuery.isError && (
          <div className="border border-orange/40 bg-orange-soft px-6 py-5">
            <div className="kicker mb-2">Erro</div>
            <h3 className="font-display text-lg font-semibold text-black mb-1">
              Falha ao carregar dashboard
            </h3>
            <p className="text-sm text-gray-600">
              {(dashboardQuery.error as Error)?.message || 'Erro desconhecido'}
            </p>
          </div>
        )}

        {dashboardQuery.isLoading && (
          <div className="border border-gray-200 bg-white px-6 py-16 text-center font-mono text-sm text-gray-600">
            carregando dashboard...
          </div>
        )}

        {dashboardQuery.data && (
          <>
            <KpiCards kpis={dashboardQuery.data.kpis} />

            <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.75fr)] gap-5">
              <TimelineChart data={dashboardQuery.data.serie_mensal} />
              <CategoryPieChart
                receitas={dashboardQuery.data.receitas_por_categoria}
                despesas={dashboardQuery.data.despesas_por_categoria}
                custos={dashboardQuery.data.custos_por_categoria}
                categorias={categoriasQuery.data || []}
                selectedCategoriaId={categoriaId}
                onCategoriaChange={setCategoriaId}
              />
            </div>

            <PaymentStatisticsPanel
              formaPagamento={
                dashboardQuery.data.receita_vendas_por_forma_pagamento
              }
              meioPagamento={
                dashboardQuery.data.receita_vendas_por_meio_pagamento
              }
              parcelas={dashboardQuery.data.receita_vendas_por_parcelas}
            />
          </>
        )}
      </div>
    </div>
  )
}

function getTodayInputValue() {
  const date = new Date()
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 10)
}

function getStartOfCurrentYear() {
  const date = new Date()
  return `${date.getFullYear()}-01-01`
}

function IconList() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M8 6h13" />
      <path d="M8 12h13" />
      <path d="M8 18h13" />
      <path d="M3 6h.01" />
      <path d="M3 12h.01" />
      <path d="M3 18h.01" />
    </svg>
  )
}
