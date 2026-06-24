import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchCategoriasFinanceiras } from '../api/categoriasFinanceiras'
import { fetchFinanceDashboard } from '../api/financeDashboard'
import {
  CategoryFiltersPanel,
  CategoryPieChart,
} from '../components/finance-dashboard/CategoryPieChart'
import { DashboardFilters } from '../components/finance-dashboard/DashboardFilters'
import { KpiCards } from '../components/finance-dashboard/KpiCards'
import { PaymentStatisticsPanel } from '../components/finance-dashboard/PaymentStatisticsPanel'
import { TimelineChart } from '../components/finance-dashboard/TimelineChart'
import { VisaoGeralTab } from '../components/finance-dashboard/VisaoGeralTab'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useDownloadPdf } from '../hooks/useDownloadPdf'
import { OPERATION_START_DATE, getTodayInputValue } from '../utils/dateRange'
import type { FinancePeriodoCategoria, TipoLancamento } from '../types/finance'

type TabKey = 'visao_geral' | 'financeiro'

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: 'visao_geral', label: 'Visão geral' },
  { key: 'financeiro', label: 'Financeiro' },
]

export function FinancePage() {
  useDocumentTitle('Finance — {{COMPANY_NAME}}')

  const [activeTab, setActiveTab] = useState<TabKey>('visao_geral')

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <FinancePageHeader />

      <nav className="mt-6 mb-5 border-b border-gray-200">
        <div className="flex items-end gap-1 overflow-x-auto">
          {TABS.map((tab) => {
            const isActive = tab.key === activeTab
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={`relative px-4 py-2.5 text-sm font-medium transition-colors ${
                  isActive ? 'text-black' : 'text-gray-500 hover:text-black'
                }`}
              >
                {tab.label}
                {isActive && (
                  <span className="absolute -bottom-px left-0 right-0 h-0.5 bg-black" />
                )}
              </button>
            )
          })}
        </div>
      </nav>

      {activeTab === 'visao_geral' && <VisaoGeralTab />}
      {activeTab === 'financeiro' && <FinanceiroTab />}
    </div>
  )
}

function FinancePageHeader() {
  return (
    <div className="flex items-start justify-between gap-6">
      <div className="min-w-0">
        <div className="kicker mb-1.5">Módulo 02</div>
        <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
          Dashboard — {`{{COMPANY_NAME}}`} Finance
        </h1>
        <p className="text-sm text-gray-600 mt-1 max-w-3xl">
          Visão geral da loja (preenchida pelo analista) e resultado consolidado
          dos lançamentos financeiros, com visão mensal, categorias e
          estatísticas de pagamento.
        </p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 bg-white text-gray-700 hover:border-black hover:text-black transition-colors"
        >
          <IconHome />
          Inicio
        </Link>
      </div>
    </div>
  )
}

function FinanceiroTab() {
  const [dataInicio, setDataInicio] = useState(OPERATION_START_DATE)
  const [dataFim, setDataFim] = useState(getTodayInputValue())
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [tipoCategoria, setTipoCategoria] = useState<TipoLancamento | ''>('')
  const { download, isDownloading } = useDownloadPdf()

  const dashboardQuery = useQuery({
    queryKey: [
      'finance-dashboard',
      { dataInicio, dataFim, categoriaId, tipoCategoria },
    ],
    queryFn: () =>
      fetchFinanceDashboard({
        data_inicio: dataInicio,
        data_fim: dataFim,
        categoria_id: categoriaId,
        tipo: tipoCategoria,
        incluir_pendentes: false,
      }),
  })

  const categoriasQuery = useQuery({
    queryKey: ['categorias-financeiras'],
    queryFn: fetchCategoriasFinanceiras,
  })

  const clearFilters = () => {
    setDataInicio(OPERATION_START_DATE)
    setDataFim(getTodayInputValue())
    setCategoriaId(null)
    setTipoCategoria('')
  }
  const visibleTimelineTypes = tipoCategoria ? [tipoCategoria] : undefined

  const handleCategoriaChange = (
    nextCategoriaId: number | null,
    periodo?: FinancePeriodoCategoria,
  ) => {
    setCategoriaId(nextCategoriaId)
    if (!periodo || nextCategoriaId === null) return

    const inicioAtual = dataInicio || periodo.data_inicio
    const fimAtual = dataFim || periodo.data_fim
    const categoriaForaDoPeriodo =
      periodo.data_inicio < inicioAtual || periodo.data_fim > fimAtual

    if (categoriaForaDoPeriodo) {
      setDataInicio(periodo.data_inicio)
      setDataFim(periodo.data_fim)
    }
  }

  const handleExportarPdf = async () => {
    await download(
      '/reports/finance/dashboard/pdf',
      {
        data_inicio: dataInicio || undefined,
        data_fim: dataFim || undefined,
        categoria_id: categoriaId ?? undefined,
      },
      `financeiro-${dataInicio || 'inicio'}_${dataFim || 'hoje'}.pdf`,
    )
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <div className="kicker">Dashboard</div>
          <h2 className="font-display text-2xl font-semibold text-black">
            Financeiro
          </h2>
          <p className="text-sm text-gray-600">
            Informações de resultados do Ecommerce da Empresa.
          </p>
        </div>

        <div className="flex flex-wrap items-end justify-between gap-3 border border-gray-200 bg-gray-50 px-4 py-3">
          <DashboardFilters
            dataInicio={dataInicio}
            dataFim={dataFim}
            onDataInicioChange={setDataInicio}
            onDataFimChange={setDataFim}
            onClear={clearFilters}
          />

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={handleExportarPdf}
              disabled={isDownloading}
              className="inline-flex items-center gap-1.5 border border-black bg-white px-3 py-1.5 text-sm text-black hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              <IconDownload />
              {isDownloading ? 'Gerando...' : 'Exportar Relatório PDF'}
            </button>

            <Link
              to="/finance/lancamentos"
              className="inline-flex items-center gap-1.5 border border-black bg-black px-3 py-1.5 text-sm text-white hover:bg-gray-900 transition-colors"
            >
              <IconList />
              Lançamentos
            </Link>
          </div>
        </div>
      </header>

      {dashboardQuery.isError && (
        <div className="border border-gray-300 bg-gray-50 px-6 py-5">
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

          <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_340px] gap-5 items-stretch">
            <div className="space-y-5 min-w-0">
              <TimelineChart
                data={dashboardQuery.data.serie_mensal}
                visibleTypes={visibleTimelineTypes}
              />

              <CategoryPieChart
                receitas={dashboardQuery.data.receitas_por_categoria}
                despesas={dashboardQuery.data.despesas_por_categoria}
                custos={dashboardQuery.data.custos_por_categoria}
              />
            </div>

            <CategoryFiltersPanel
              receitas={dashboardQuery.data.receitas_por_categoria}
              despesas={dashboardQuery.data.despesas_por_categoria}
              custos={dashboardQuery.data.custos_por_categoria}
              categorias={categoriasQuery.data || []}
              periodosPorCategoria={
                dashboardQuery.data.periodos_por_categoria || []
              }
              selectedCategoriaId={categoriaId}
              onCategoriaChange={handleCategoriaChange}
              selectedTipo={tipoCategoria}
              onTipoChange={setTipoCategoria}
            />
          </div>

          <PaymentStatisticsPanel
            formaPagamento={
              dashboardQuery.data.receita_vendas_por_forma_pagamento
            }
            meioPagamento={
              dashboardQuery.data.receita_vendas_por_meio_pagamento
            }
          />
        </>
      )}
    </div>
  )
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

function IconHome() {
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
      <path d="m3 10.5 9-7 9 7" />
      <path d="M5 10v10h14V10" />
      <path d="M9 20v-6h6v6" />
    </svg>
  )
}

function IconDownload() {
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
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="M7 10l5 5 5-5" />
      <path d="M12 15V3" />
    </svg>
  )
}
