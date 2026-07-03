import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AgGridReact } from 'ag-grid-react'
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
  type GridOptions,
} from 'ag-grid-community'

import { fetchVariacoes } from '../../api/variacoes'
import { ExportPdfModal } from '../reports/ExportPdfModal'
import { useDownloadPdf } from '../../hooks/useDownloadPdf'
import type { Variacao } from '../../types/catalog'
import { COLUNAS_CATALOGO } from '../../types/reports'
import { formatDateTimeBR } from '../../utils/dateRange'
import { MoneyCellRenderer } from './MoneyCellRenderer'
import { PercentCellRenderer } from './PercentCellRenderer'
import { StatusBadgeRenderer } from './StatusBadgeRenderer'
import { AcoesCellRenderer } from './AcoesCellRenderer'

ModuleRegistry.registerModules([AllCommunityModule])

import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

export function CatalogoGrid() {
  const [searchText, setSearchText] = useState('')
  const [mostrarArquivados, setMostrarArquivados] = useState(false)
  const [isExportOpen, setIsExportOpen] = useState(false)
  const { download, isDownloading } = useDownloadPdf()

  const {
    data: variacoes = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['variacoes', { arquivados: mostrarArquivados }],
    queryFn: () => fetchVariacoes({ inativos: mostrarArquivados }),
  })

  // Em "Arquivados", a API traz ativas + inativas; filtramos só as arquivadas.
  const rowData = useMemo(
    () => (mostrarArquivados ? variacoes.filter((v) => !v.ativo) : variacoes),
    [variacoes, mostrarArquivados],
  )

  const ultimaAtualizacao = useMemo(() => {
    let max: string | null = null
    for (const v of variacoes) {
      if (v.atualizado_em && (max === null || v.atualizado_em > max)) {
        max = v.atualizado_em
      }
    }
    return formatDateTimeBR(max)
  }, [variacoes])

  const columnDefs = useMemo<ColDef<Variacao>[]>(
    () => [
      {
        field: 'sku_nuvemshop',
        headerName: 'SKU',
        width: 150,
        flex: 0,
        cellClass: 'font-mono text-xs',
        tooltipField: 'sku_nuvemshop',
      },
      {
        field: 'produto_descricao_site',
        headerName: 'Descrição (NuvemShop)',
        minWidth: 240,
        flex: 1,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
      },
      {
        field: 'produto_descricao_gestaoclick',
        headerName: 'Descrição (GestãoClick)',
        minWidth: 240,
        flex: 1,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
      },
      {
        field: 'descricao',
        headerName: 'Variação',
        width: 120,
        flex: 0,
        tooltipField: 'descricao',
      },
      {
        field: 'custo',
        headerName: 'Custo',
        width: 120,
        flex: 0,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_loja',
        headerName: 'Preço Loja',
        width: 125,
        flex: 0,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_site',
        headerName: 'Preço Site',
        width: 125,
        flex: 0,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_promocional',
        headerName: 'Preço Promocional',
        width: 150,
        flex: 0,
        cellClass: 'promo-price-cell',
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'margem_percentual',
        headerName: 'Margem %',
        width: 120,
        flex: 0,
        cellRenderer: PercentCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'margem_promocional_percentual',
        headerName: 'Margem Promoção',
        width: 140,
        flex: 0,
        cellClass: 'promo-margin-cell',
        cellRenderer: PercentCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'status_nuvemshop',
        headerName: 'Status NS',
        width: 120,
        flex: 0,
        cellRenderer: StatusBadgeRenderer,
        filter: 'agTextColumnFilter',
      },
      {
        field: 'status_integracao',
        headerName: 'Status Int.',
        width: 120,
        flex: 0,
        cellRenderer: StatusBadgeRenderer,
        filter: 'agTextColumnFilter',
      },
      {
        headerName: 'Ações',
        cellRenderer: AcoesCellRenderer,
        width: 200,
        flex: 0,
        sortable: false,
        filter: false,
        pinned: 'right',
      },
    ],
    [],
  )

  const defaultColDef = useMemo<ColDef>(
    () => ({
      flex: 1,
      minWidth: 100,
      resizable: true,
      sortable: true,
      filter: 'agTextColumnFilter',
      floatingFilter: true,
    }),
    [],
  )

  const gridOptions = useMemo<GridOptions<Variacao>>(
    () => ({
      rowHeight: 38,
      headerHeight: 40,
      floatingFiltersHeight: 36,
      pagination: true,
      paginationPageSize: 50,
      paginationPageSizeSelector: [25, 50, 100, 200],
      quickFilterText: searchText,
      enableCellTextSelection: true,
      ensureDomOrder: true,
      localeText: {
        page: 'Página',
        to: 'até',
        of: 'de',
        next: 'Próxima',
        last: 'Última',
        first: 'Primeira',
        previous: 'Anterior',
        noRowsToShow: 'Sem variações para exibir',
        loadingOoo: 'Carregando...',
        filterOoo: 'Filtrar...',
        contains: 'Contém',
        equals: 'Igual a',
        notEqual: 'Diferente de',
        startsWith: 'Começa com',
        endsWith: 'Termina com',
        blank: 'Vazio',
        notBlank: 'Preenchido',
        andCondition: 'E',
        orCondition: 'OU',
        applyFilter: 'Aplicar',
        resetFilter: 'Limpar',
        clearFilter: 'Limpar',
        cancelFilter: 'Cancelar',
        group: 'Grupo',
        selectAll: 'Selecionar tudo',
        searchOoo: 'Buscar...',
      },
      animateRows: true,
    }),
    [searchText],
  )

  const handleExport = async (colunas: string[]) => {
    await download(
      '/reports/catalog/pdf',
      {
        colunas,
        incluir_inativos: mostrarArquivados,
        busca: searchText || undefined,
      },
      `ecommerce-catalogo-${new Date().toISOString().slice(0, 10)}.pdf`,
    )
    setIsExportOpen(false)
  }

  if (isError) {
    return (
      <div className="border border-gray-300 bg-gray-50 px-6 py-5">
        <div className="kicker mb-2">Erro</div>
        <h3 className="font-display text-lg font-semibold text-black mb-1">
          Falha ao carregar variações
        </h3>
        <p className="text-sm text-gray-600">
          {(error as Error)?.message || 'Erro desconhecido'}
        </p>
      </div>
    )
  }

  return (
    <div className="border border-gray-200 bg-white">
      <div className="flex items-center gap-4 px-4 py-3 border-b border-gray-200">
        <div className="relative flex-1 max-w-md">
          <input
            type="text"
            placeholder="Buscar em todas as colunas..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors"
          />
        </div>

        <button
          type="button"
          onClick={() => setMostrarArquivados((v) => !v)}
          aria-pressed={mostrarArquivados}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border transition-colors ${
            mostrarArquivados
              ? 'border-black bg-black text-white hover:bg-gray-900'
              : 'border-gray-200 text-gray-700 hover:border-black hover:text-black'
          }`}
        >
          <IconArchive />
          Arquivados
        </button>

        <button
          type="button"
          onClick={() => setIsExportOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-black text-black hover:bg-gray-50 transition-colors"
        >
          <IconDownload />
          Exportar PDF
        </button>

        <div className="ml-auto flex flex-col items-end gap-0.5">
          <div className="font-mono text-xs text-gray-600 tabular-nums">
            {isLoading
              ? 'carregando...'
              : `${rowData.length.toLocaleString('pt-BR')} ${
                  mostrarArquivados ? 'arquivadas' : 'variações'
                }`}
          </div>
          {ultimaAtualizacao && (
            <div className="font-mono text-xs text-gray-500">
              Última atualização: {ultimaAtualizacao}
            </div>
          )}
        </div>
      </div>

      <div
        className="ag-theme-quartz ecommerce-grid ecommerce-catalog-grid"
        style={{ height: 'calc(100vh - 240px)', minHeight: 500 }}
      >
        <AgGridReact<Variacao>
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          gridOptions={gridOptions}
          loading={isLoading}
          getRowId={(params) => String(params.data.id)}
        />
      </div>

      <ExportPdfModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        titulo="Exportar — Catálogo"
        colunasDisponiveis={COLUNAS_CATALOGO}
        onConfirm={handleExport}
        isDownloading={isDownloading}
      />
    </div>
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

function IconArchive() {
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
      <rect x="2" y="3" width="20" height="5" />
      <path d="M4 8v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </svg>
  )
}
