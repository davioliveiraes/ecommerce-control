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
import { MoneyCellRenderer } from './MoneyCellRenderer'
import { PercentCellRenderer } from './PercentCellRenderer'
import { StatusBadgeRenderer } from './StatusBadgeRenderer'
import { AcoesCellRenderer } from './AcoesCellRenderer'

ModuleRegistry.registerModules([AllCommunityModule])

import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

export function CatalogoGrid() {
  const [searchText, setSearchText] = useState('')
  const [incluirInativos, setIncluirInativos] = useState(false)
  const [isExportOpen, setIsExportOpen] = useState(false)
  const [apenasPromocional, setApenasPromocional] = useState(false)
  const { download, isDownloading } = useDownloadPdf()

  const {
    data: variacoes = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['variacoes', { inativos: incluirInativos }],
    queryFn: () => fetchVariacoes({ inativos: incluirInativos }),
  })

  const columnDefs = useMemo<ColDef<Variacao>[]>(
    () => [
      {
        field: 'sku_nuvemshop',
        headerName: 'SKU',
        minWidth: 200,
        flex: 0,
        cellClass: 'font-mono text-xs',
        tooltipField: 'sku_nuvemshop',
      },
      {
        colId: 'descricao_site_group',
        field: 'produto_descricao_site',
        rowGroup: true,
        hide: true,
      },
      {
        field: 'produto_descricao_gestaoclick',
        headerName: 'Descrição (GestãoClick)',
        minWidth: 260,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
      },
      {
        colId: 'descricao_nuvemshop',
        field: 'produto_descricao_site',
        headerName: 'Descrição (NuvemShop)',
        minWidth: 280,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
      },
      {
        field: 'descricao',
        headerName: 'Variação',
        minWidth: 140,
        tooltipField: 'descricao',
      },
      {
        field: 'custo',
        headerName: 'Custo',
        minWidth: 110,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_loja',
        headerName: 'Preço Loja',
        minWidth: 110,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_site',
        headerName: 'Preço Site',
        minWidth: 110,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'preco_promocional',
        headerName: 'Preço Promocional',
        minWidth: 150,
        cellClass: 'promo-price-cell',
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'margem_percentual',
        headerName: 'Margem %',
        minWidth: 110,
        cellRenderer: PercentCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'margem_promocional_percentual',
        headerName: 'Margem Promoção',
        minWidth: 145,
        cellClass: 'promo-margin-cell',
        cellRenderer: PercentCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'status_nuvemshop',
        headerName: 'Status NS',
        minWidth: 120,
        cellRenderer: StatusBadgeRenderer,
        filter: 'agSetColumnFilter',
      },
      {
        field: 'status_integracao',
        headerName: 'Status Int.',
        minWidth: 120,
        cellRenderer: StatusBadgeRenderer,
        filter: 'agSetColumnFilter',
      },
      {
        headerName: 'Ações',
        cellRenderer: AcoesCellRenderer,
        minWidth: 170,
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
      suppressClickEdit: true,
      singleClickEdit: false,
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
      autoGroupColumnDef: {
        headerName: 'Produto',
        minWidth: 320,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
        cellRendererParams: {
          suppressCount: false,
        },
      },
      groupDisplayType: 'singleColumn',
      groupDefaultExpanded: 0,
      animateRows: true,
    }),
    [searchText],
  )

  const handleExport = async (colunas: string[]) => {
    await download(
      '/reports/catalog/pdf',
      {
        colunas,
        incluir_inativos: incluirInativos,
        apenas_promocional: apenasPromocional,
        busca: searchText || undefined,
      },
      `ecommerce-catalogo-${new Date().toISOString().slice(0, 10)}.pdf`,
    )
    setIsExportOpen(false)
  }

  const filtrosExtrasModal = (
    <label className="flex cursor-pointer items-center gap-2 text-sm text-gray-700">
      <input
        type="checkbox"
        checked={apenasPromocional}
        onChange={(e) => setApenasPromocional(e.target.checked)}
        className="accent-black"
      />
      Apenas variações com preço promocional
    </label>
  )

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

        <label className="flex items-center gap-2 text-sm text-gray-600 select-none cursor-pointer">
          <input
            type="checkbox"
            checked={incluirInativos}
            onChange={(e) => setIncluirInativos(e.target.checked)}
            className="accent-black"
          />
          Incluir inativos
        </label>

        <button
          type="button"
          onClick={() => setIsExportOpen(true)}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-black text-black hover:bg-gray-50 transition-colors"
        >
          <IconDownload />
          Exportar PDF
        </button>

        <div className="font-mono text-xs text-gray-600 tabular-nums">
          {isLoading
            ? 'carregando...'
            : `${variacoes.length.toLocaleString('pt-BR')} variações`}
        </div>
      </div>

      <div
        className="ag-theme-quartz ecommerce-grid ecommerce-catalog-grid"
        style={{ height: 'calc(100vh - 240px)', minHeight: 500 }}
      >
        <AgGridReact<Variacao>
          rowData={variacoes}
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
        titulo="Exportar — {{COMPANY_NAME}} Catálogo"
        colunasDisponiveis={COLUNAS_CATALOGO}
        filtrosExtras={filtrosExtrasModal}
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
