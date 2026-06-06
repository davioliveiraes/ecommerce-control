import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchCategoriasFinanceiras } from '../api/categoriasFinanceiras'
import { fetchFinanceDashboard } from '../api/financeDashboard'
import { AnalyticsOverview } from '../components/finance-dashboard/AnalyticsOverview'
import { AnalyticsProducts } from '../components/finance-dashboard/AnalyticsProducts'
import { ExportPdfModal } from '../components/reports/ExportPdfModal'
import {
  CategoryFiltersPanel,
  CategoryPieChart,
} from '../components/finance-dashboard/CategoryPieChart'
import { DashboardFilters } from '../components/finance-dashboard/DashboardFilters'
import { KpiCards } from '../components/finance-dashboard/KpiCards'
import { PaymentStatisticsPanel } from '../components/finance-dashboard/PaymentStatisticsPanel'
import { StoreOverviewPanel } from '../components/finance-dashboard/StoreOverviewPanel'
import { TimelineChart } from '../components/finance-dashboard/TimelineChart'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useDownloadPdf } from '../hooks/useDownloadPdf'
import type { FinancePeriodoCategoria, TipoLancamento } from '../types/finance'
import { COLUNAS_FINANCE } from '../types/reports'

type TabKey = 'financeiro' | 'visao_geral' | 'produtos'

const TABS: Array<{ key: TabKey; label: string; description: string }> = [
  {
    key: 'financeiro',
    label: 'Financeiro',
    description: 'Receita, custo, despesa e lucro consolidados.',
  },
  {
    key: 'visao_geral',
    label: 'Visão geral',
    description: 'Visitas, comportamento e conversões da loja.',
  },
  {
    key: 'produtos',
    label: 'Produtos',
    description: 'Rankings de vendas, visualizações, estoque e margem.',
  },
]

export function FinancePage() {
  useDocumentTitle('Finance — {{COMPANY_NAME}}')

  const [activeTab, setActiveTab] = useState<TabKey>('financeiro')

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
                  isActive
                    ? 'text-black'
                    : 'text-gray-500 hover:text-black'
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

      {activeTab === 'financeiro' && <FinanceiroTab />}
      {activeTab === 'visao_geral' && <AnalyticsOverview />}
      {activeTab === 'produtos' && <AnalyticsProducts />}
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
          Resultado consolidado dos lançamentos financeiros, com visão mensal,
          estatísticas da loja e rankings de produtos.
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

        <Link
          to="/finance/lancamentos"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors"
        >
          <IconList />
          Lançamentos
        </Link>
      </div>
    </div>
  )
}

function FinanceiroTab() {
  const [dataInicio, setDataInicio] = useState(getStartOfCurrentYear())
  const [dataFim, setDataFim] = useState(getTodayInputValue())
  const [incluirPendentes, setIncluirPendentes] = useState(false)
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [tipoCategoria, setTipoCategoria] = useState<TipoLancamento | ''>('')
  const [isExportOpen, setIsExportOpen] = useState(false)
  const { download, isDownloading } = useDownloadPdf()

  const dashboardQuery = useQuery({
    queryKey: [
      'finance-dashboard',
      { dataInicio, dataFim, incluirPendentes, categoriaId, tipoCategoria },
    ],
    queryFn: () =>
      fetchFinanceDashboard({
        data_inicio: dataInicio,
        data_fim: dataFim,
        categoria_id: categoriaId,
        tipo: tipoCategoria,
        incluir_pendentes: incluirPendentes,
      }),
  })

  const categoriasQuery = useQuery({
    queryKey: ['categorias-financeiras'],
    queryFn: fetchCategoriasFinanceiras,
  })

  const clearFilters = () => {
    const periodoGeral = dashboardQuery.data?.periodo_geral
    setDataInicio(periodoGeral?.data_inicio || '')
    setDataFim(periodoGeral?.data_fim || '')
    setCategoriaId(null)
    setTipoCategoria('')
    setIncluirPendentes(true)
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

  const handleExport = async (colunas: string[]) => {
    await download(
      '/reports/finance/pdf',
      {
        colunas,
        data_inicio: dataInicio || undefined,
        data_fim: dataFim || undefined,
        tipo: tipoCategoria || undefined,
        categoria_id: categoriaId ?? undefined,
        status: incluirPendentes ? undefined : 'PAGO',
      },
      `ecommerce-finance-dashboard-${new Date().toISOString().slice(0, 10)}.pdf`,
    )
    setIsExportOpen(false)
  }

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-3">
        <DashboardFilters
          dataInicio={dataInicio}
          dataFim={dataFim}
          incluirPendentes={incluirPendentes}
          onDataInicioChange={setDataInicio}
          onDataFimChange={setDataFim}
          onIncluirPendentesChange={setIncluirPendentes}
          onClear={clearFilters}
        />

        <button
          type="button"
          onClick={() => setIsExportOpen(true)}
          className="inline-flex shrink-0 items-center gap-1.5 px-4 py-2 text-sm border border-black text-black hover:bg-gray-50 transition-colors"
        >
          <IconDownload />
          Exportar PDF
        </button>
      </div>

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

          <StoreOverviewPanel />

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

      <ExportPdfModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        titulo="Relatório — {{COMPANY_NAME}} Finance"
        colunasDisponiveis={COLUNAS_FINANCE}
        onConfirm={handleExport}
        isDownloading={isDownloading}
      />
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
