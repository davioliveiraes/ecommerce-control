import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AgGridReact } from 'ag-grid-react'
import {
  AllCommunityModule,
  ModuleRegistry,
  type ColDef,
  type GridOptions,
} from 'ag-grid-community'

import { fetchLancamentosFinanceiros } from '../../api/lancamentosFinanceiros'
import type {
  LancamentoFinanceiro,
  StatusLancamento,
  TipoLancamento,
} from '../../types/finance'
import { MoneyCellRenderer } from '../catalogo/MoneyCellRenderer'
import { AcoesLancamentoCellRenderer } from './AcoesLancamentoCellRenderer'
import { CategoriaFinanceiraCellRenderer } from './CategoriaFinanceiraCellRenderer'
import { DateCellRenderer } from './DateCellRenderer'
import { StatusLancamentoBadgeRenderer } from './StatusLancamentoBadgeRenderer'
import { TipoLancamentoBadgeRenderer } from './TipoLancamentoBadgeRenderer'

ModuleRegistry.registerModules([AllCommunityModule])

import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-quartz.css'

export function LancamentosFinanceirosGrid() {
  const [searchText, setSearchText] = useState('')
  const [incluirArquivados, setIncluirArquivados] = useState(false)
  const [tipo, setTipo] = useState<TipoLancamento | ''>('')
  const [status, setStatus] = useState<StatusLancamento | ''>('')

  const {
    data: lancamentos = [],
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: [
      'lancamentos-financeiros',
      { q: searchText, inativos: incluirArquivados, tipo, status },
    ],
    queryFn: () =>
      fetchLancamentosFinanceiros({
        q: searchText,
        inativos: incluirArquivados,
        tipo,
        status,
      }),
  })

  const columnDefs = useMemo<ColDef<LancamentoFinanceiro>[]>(
    () => [
      {
        field: 'descricao',
        headerName: 'Descrição',
        minWidth: 260,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug',
        tooltipField: 'descricao',
      },
      {
        field: 'categoria_nome',
        headerName: 'Categoria',
        minWidth: 180,
        cellRenderer: CategoriaFinanceiraCellRenderer,
      },
      {
        field: 'tipo',
        headerName: 'Tipo',
        minWidth: 150,
        cellRenderer: TipoLancamentoBadgeRenderer,
      },
      {
        field: 'valor',
        headerName: 'Valor',
        minWidth: 120,
        cellRenderer: MoneyCellRenderer,
        type: 'numericColumn',
      },
      {
        field: 'data_lancamento',
        headerName: 'Vencimento',
        minWidth: 130,
        cellRenderer: DateCellRenderer,
        filter: 'agDateColumnFilter',
      },
      {
        field: 'status',
        headerName: 'Status',
        minWidth: 130,
        cellRenderer: StatusLancamentoBadgeRenderer,
      },
      {
        field: 'forma_pagamento',
        headerName: 'Forma pgto.',
        minWidth: 150,
        valueFormatter: (params) => formatFormaPagamento(params.value),
      },
      {
        field: 'meio_pagamento',
        headerName: 'Meio pgto.',
        minWidth: 150,
        valueFormatter: (params) => formatMeioPagamento(params.value),
      },
      {
        field: 'quantidade_parcelas',
        headerName: 'Parcelas',
        minWidth: 110,
        valueFormatter: (params) => (params.value ? `${params.value}x` : '—'),
        type: 'numericColumn',
      },
      {
        field: 'quantidade_vendas',
        headerName: 'Vendas',
        minWidth: 110,
        valueFormatter: (params) => {
          if (params.data?.tipo !== 'RECEITA') return ''
          return params.value ? params.value.toLocaleString('pt-BR') : ''
        },
        type: 'numericColumn',
      },
      {
        field: 'fonte_trafego',
        headerName: 'Fonte tráfego',
        minWidth: 150,
        valueFormatter: (params) => params.value || '—',
        tooltipField: 'fonte_trafego',
      },
      {
        field: 'observacoes',
        headerName: 'Observações',
        minWidth: 220,
        wrapText: true,
        autoHeight: true,
        cellClass: 'ag-cell-wrap-text leading-snug text-gray-600',
        tooltipField: 'observacoes',
      },
      {
        headerName: 'Ações',
        cellRenderer: AcoesLancamentoCellRenderer,
        minWidth: 230,
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

  const gridOptions = useMemo<GridOptions<LancamentoFinanceiro>>(
    () => ({
      theme: 'legacy',
      rowHeight: 38,
      headerHeight: 40,
      floatingFiltersHeight: 36,
      pagination: true,
      paginationPageSize: 50,
      paginationPageSizeSelector: [25, 50, 100, 200],
      quickFilterText: searchText,
      localeText: {
        page: 'Página',
        to: 'até',
        of: 'de',
        next: 'Próxima',
        last: 'Última',
        first: 'Primeira',
        previous: 'Anterior',
        noRowsToShow: 'Sem lançamentos para exibir',
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
        selectAll: 'Selecionar tudo',
        searchOoo: 'Buscar...',
      },
      animateRows: true,
    }),
    [searchText],
  )

  const total = useMemo(() => {
    return lancamentos.reduce((acc, lancamento) => {
      const value = parseFloat(lancamento.valor)
      if (isNaN(value) || !lancamento.ativo) return acc
      return lancamento.tipo === 'RECEITA' ? acc + value : acc - value
    }, 0)
  }, [lancamentos])

  if (isError) {
    return (
      <div className="border border-gray-300 bg-gray-50 px-6 py-5">
        <div className="kicker mb-2">Erro</div>
        <h3 className="font-display text-lg font-semibold text-black mb-1">
          Falha ao carregar lançamentos
        </h3>
        <p className="text-sm text-gray-600">
          {(error as Error)?.message || 'Erro desconhecido'}
        </p>
      </div>
    )
  }

  return (
    <div className="border border-gray-200 bg-white">
      <div className="flex flex-wrap items-center gap-3 px-4 py-3 border-b border-gray-200">
        <div className="relative flex-1 min-w-64 max-w-md">
          <input
            type="text"
            placeholder="Buscar descrição ou observações..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="w-full px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors"
          />
        </div>

        <select
          value={tipo}
          onChange={(e) => setTipo(e.target.value as TipoLancamento | '')}
          className="px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors"
        >
          <option value="">Todos os tipos</option>
          <option value="RECEITA">Entradas</option>
          <option value="DESPESA">Saídas · despesas</option>
          <option value="CUSTO">Saídas · custos</option>
        </select>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as StatusLancamento | '')}
          className="px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors"
        >
          <option value="">Todos os status</option>
          <option value="PENDENTE">Pendentes</option>
          <option value="PAGO">Pagos</option>
        </select>

        <label className="flex items-center gap-2 text-sm text-gray-600 select-none cursor-pointer">
          <input
            type="checkbox"
            checked={incluirArquivados}
            onChange={(e) => setIncluirArquivados(e.target.checked)}
            className="accent-black"
          />
          Incluir arquivados
        </label>

        <div className="ml-auto font-mono text-xs text-gray-600 tabular-nums">
          {isLoading
            ? 'carregando...'
            : `${lancamentos.length.toLocaleString('pt-BR')} lançamentos · ${new Intl.NumberFormat(
                'pt-BR',
                { style: 'currency', currency: 'BRL' },
              ).format(total)}`}
        </div>
      </div>

      <div
        className="ag-theme-quartz ecommerce-grid"
        style={{ height: 'calc(100vh - 260px)', minHeight: 500 }}
      >
        <AgGridReact<LancamentoFinanceiro>
          rowData={lancamentos}
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          gridOptions={gridOptions}
          loading={isLoading}
          getRowId={(params) => String(params.data.id)}
        />
      </div>
    </div>
  )
}

function formatFormaPagamento(value?: string) {
  const labels: Record<string, string> = {
    PIX: 'Pix',
    CARTAO_CREDITO: 'Cartão de crédito',
    BOLETO: 'Boleto',
    NUVEMPAGO: 'NuvemPago',
    OUTRO: 'Outro',
  }
  return value ? labels[value] || value : '—'
}

function formatMeioPagamento(value?: string) {
  const labels: Record<string, string> = {
    NUVEMPAGO: 'NuvemPago',
    MERCADO_PAGO: 'Mercado Pago',
    PAGSEGURO: 'PagSeguro',
    MANUAL: 'Manual',
    OUTRO: 'Outro',
  }
  return value ? labels[value] || value : '—'
}
