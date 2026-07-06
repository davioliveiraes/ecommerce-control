import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchCategoriasFinanceiras } from '../api/categoriasFinanceiras'
import { fetchFinanceDashboard } from '../api/financeDashboard'
import { fetchVisaoGeralPeriodos } from '../api/visaoGeral'
import { CategoryPieChart } from '../components/finance-dashboard/CategoryPieChart'
import { FinanceiroFiltros } from '../components/finance-dashboard/FinanceiroFiltros'
import { KpiCards } from '../components/finance-dashboard/KpiCards'
import { TimelineChart } from '../components/finance-dashboard/TimelineChart'
import { VisaoGeralTab } from '../components/finance-dashboard/VisaoGeralTab'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useDownloadPdf } from '../hooks/useDownloadPdf'
import {
  formatDateBR,
  getAnosDisponiveis,
  intervaloDoAno,
  intervaloDoMes,
} from '../utils/dateRange'
import type { FinancePeriodoCategoria, TipoLancamento } from '../types/finance'

type TabKey = 'visao_geral' | 'financeiro'

const TABS: Array<{ key: TabKey; label: string }> = [
  { key: 'visao_geral', label: 'Visão geral' },
  { key: 'financeiro', label: 'Finanças Gerais' },
]

export function FinancePage() {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''

  useDocumentTitle(nomeEmpresa ? `Financeiro — ${nomeEmpresa}` : 'Financeiro')

  const [activeTab, setActiveTab] = useState<TabKey>('visao_geral')

  // Filtro de período da Visão geral, elevado para cá para que o botão
  // "Exportar Relatório" do cabeçalho use o mesmo intervalo aplicado no filtro.
  const anosDisponiveis = useMemo(() => getAnosDisponiveis(), [])
  const hoje = useMemo(() => new Date(), [])
  const [ano, setAno] = useState(() => hoje.getFullYear())
  // mes = 0-11, ou null para "Ano inteiro".
  const [mes, setMes] = useState<number | null>(null)

  const { dataInicio, dataFim } = useMemo(
    () => (mes === null ? intervaloDoAno(ano) : intervaloDoMes(ano, mes)),
    [ano, mes],
  )

  const clearFilters = () => {
    setAno(hoje.getFullYear())
    setMes(null)
  }

  // Última atualização = período mais recente cadastrado na Visão geral.
  // A query é compartilhada (mesma queryKey) com a VisaoGeralTab via cache.
  const visaoGeralQuery = useQuery({
    queryKey: ['visao-geral-periodos'],
    queryFn: fetchVisaoGeralPeriodos,
  })
  const visaoGeralUltimaAtualizacao = formatDateBR(
    visaoGeralQuery.data?.[0]?.data_fim,
  )

  // A "última atualização" do Financeiro vem do dashboard (dentro do FinanceiroTab);
  // o tab reporta o valor para cá para exibirmos no canto da barra de abas.
  const [financeiroUltimaAtualizacao, setFinanceiroUltimaAtualizacao] =
    useState<string | null>(null)

  const ultimaAtualizacao =
    activeTab === 'visao_geral'
      ? visaoGeralUltimaAtualizacao
      : financeiroUltimaAtualizacao

  // Parâmetros de exportação do Financeiro, reportados pelo FinanceiroTab, para
  // que o botão "Exportar Relatório" do cabeçalho funcione também nessa aba.
  const [financeiroExport, setFinanceiroExport] = useState<{
    dataInicio: string
    dataFim: string
    categoriaId: number | null
  } | null>(null)

  const { download, isDownloading } = useDownloadPdf()

  const handleExport = async () => {
    if (activeTab === 'visao_geral') {
      await download(
        '/reports/visao-geral/pdf',
        {
          data_inicio: dataInicio || undefined,
          data_fim: dataFim || undefined,
        },
        `visao-geral-${dataInicio || 'inicio'}_${dataFim || 'hoje'}.pdf`,
      )
      return
    }

    if (financeiroExport) {
      await download(
        '/reports/finance/dashboard/pdf',
        {
          data_inicio: financeiroExport.dataInicio || undefined,
          data_fim: financeiroExport.dataFim || undefined,
          categoria_id: financeiroExport.categoriaId ?? undefined,
        },
        `financeiro-${financeiroExport.dataInicio || 'inicio'}_${financeiroExport.dataFim || 'hoje'}.pdf`,
      )
    }
  }

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <FinancePageHeader onExport={handleExport} isExporting={isDownloading} />

      <nav className="mt-6 mb-5 border-b border-gray-200">
        <div className="flex items-end justify-between gap-4">
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

          {ultimaAtualizacao && (
            <div className="shrink-0 pb-2.5 font-mono text-xs text-gray-500">
              Última atualização: {ultimaAtualizacao}
            </div>
          )}
        </div>
      </nav>

      {activeTab === 'visao_geral' && (
        <VisaoGeralTab
          ano={ano}
          mes={mes}
          anos={anosDisponiveis}
          onAnoChange={setAno}
          onMesChange={setMes}
          onClear={clearFilters}
          dataInicio={dataInicio}
          dataFim={dataFim}
        />
      )}
      {activeTab === 'financeiro' && (
        <FinanceiroTab
          onUltimaAtualizacaoChange={setFinanceiroUltimaAtualizacao}
          onExportParamsChange={setFinanceiroExport}
        />
      )}
    </div>
  )
}

interface FinancePageHeaderProps {
  onExport: () => void
  isExporting: boolean
}

function FinancePageHeader({ onExport, isExporting }: FinancePageHeaderProps) {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''

  return (
    <div className="flex items-start justify-between gap-6">
      <div className="min-w-0">
        <div className="kicker mb-1.5">Módulo 02</div>
        <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
          Dashboard Financeiro — {nomeEmpresa}
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
        <button
          type="button"
          onClick={onExport}
          disabled={isExporting}
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 bg-white text-gray-700 hover:border-black hover:text-black transition-colors disabled:opacity-50"
        >
          <IconDownload />
          {isExporting ? 'Gerando...' : 'Exportar Relatório PDF'}
        </button>
      </div>
    </div>
  )
}

interface FinanceiroTabProps {
  onUltimaAtualizacaoChange: (value: string | null) => void
  onExportParamsChange: (params: {
    dataInicio: string
    dataFim: string
    categoriaId: number | null
  }) => void
}

function FinanceiroTab({
  onUltimaAtualizacaoChange,
  onExportParamsChange,
}: FinanceiroTabProps) {
  const anosDisponiveis = useMemo(() => getAnosDisponiveis(), [])
  const hoje = useMemo(() => new Date(), [])
  const [ano, setAno] = useState(() => hoje.getFullYear())
  // mes = 0-11, ou null para "Ano inteiro".
  const [mes, setMes] = useState<number | null>(null)
  const [categoriaId, setCategoriaId] = useState<number | null>(null)
  const [tipoCategoria, setTipoCategoria] = useState<TipoLancamento | ''>('')

  const { dataInicio, dataFim } = useMemo(
    () => (mes === null ? intervaloDoAno(ano) : intervaloDoMes(ano, mes)),
    [ano, mes],
  )

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
    setAno(hoje.getFullYear())
    setMes(null)
    setCategoriaId(null)
    setTipoCategoria('')
  }
  const visibleTimelineTypes = tipoCategoria ? [tipoCategoria] : undefined

  // Reporta a última atualização para a página exibir no canto da barra de abas.
  useEffect(() => {
    onUltimaAtualizacaoChange(
      formatDateBR(dashboardQuery.data?.periodo_geral?.data_fim),
    )
  }, [dashboardQuery.data, onUltimaAtualizacaoChange])

  // Reporta os parâmetros de exportação para o botão do cabeçalho.
  useEffect(() => {
    onExportParamsChange({ dataInicio, dataFim, categoriaId })
  }, [dataInicio, dataFim, categoriaId, onExportParamsChange])

  const handleCategoriaChange = (
    nextCategoriaId: number | null,
    periodo?: FinancePeriodoCategoria,
  ) => {
    setCategoriaId(nextCategoriaId)
    if (!periodo || nextCategoriaId === null) return

    const categoriaForaDoPeriodo =
      periodo.data_inicio < dataInicio || periodo.data_fim > dataFim

    if (categoriaForaDoPeriodo) {
      // Expande para o ano inteiro que contém o período da categoria.
      setAno(Number(periodo.data_inicio.slice(0, 4)))
      setMes(null)
    }
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <div className="kicker">Dashboard</div>
          <h2 className="font-display text-2xl font-semibold text-black">
            Finanças Gerais
          </h2>
          <p className="text-sm text-gray-600">
            Informações de resultados do Ecommerce da Empresa.
          </p>
        </div>

        <div className="flex flex-wrap items-end justify-between gap-3 border border-gray-200 bg-gray-50 px-4 py-3">
          <FinanceiroFiltros
            ano={ano}
            mes={mes}
            anos={anosDisponiveis}
            onAnoChange={setAno}
            onMesChange={setMes}
            categorias={categoriasQuery.data || []}
            periodosPorCategoria={dashboardQuery.data?.periodos_por_categoria || []}
            selectedCategoriaId={categoriaId}
            onCategoriaChange={handleCategoriaChange}
            selectedTipo={tipoCategoria}
            onTipoChange={setTipoCategoria}
            onClear={clearFilters}
          />

          <div className="flex flex-wrap items-center gap-2">
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
