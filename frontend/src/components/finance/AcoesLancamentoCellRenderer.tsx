import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { ICellRendererParams } from 'ag-grid-community'

import {
  archiveLancamentoFinanceiro,
  marcarLancamentoPago,
  restoreLancamentoFinanceiro,
} from '../../api/lancamentosFinanceiros'
import type { LancamentoFinanceiro } from '../../types/finance'

export function AcoesLancamentoCellRenderer(
  params: ICellRendererParams<LancamentoFinanceiro>,
) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['lancamentos-financeiros'] })
    queryClient.invalidateQueries({ queryKey: ['finance-dashboard'] })
  }

  const archiveMutation = useMutation({
    mutationFn: archiveLancamentoFinanceiro,
    onSuccess: invalidate,
  })

  const restoreMutation = useMutation({
    mutationFn: restoreLancamentoFinanceiro,
    onSuccess: invalidate,
  })

  const markPaidMutation = useMutation({
    mutationFn: marcarLancamentoPago,
    onSuccess: invalidate,
  })

  if (!params.data) return null

  const lancamento = params.data
  const isBusy =
    archiveMutation.isPending ||
    restoreMutation.isPending ||
    markPaidMutation.isPending

  const handleEditar = () => {
    navigate(`/finance/lancamentos/${lancamento.id}/editar`)
  }

  const handleArquivar = () => {
    if (confirm(`Arquivar lançamento "${lancamento.descricao}"?`)) {
      archiveMutation.mutate(lancamento.id)
    }
  }

  const handleRestaurar = () => {
    restoreMutation.mutate(lancamento.id)
  }

  const handleMarcarPago = () => {
    markPaidMutation.mutate(lancamento.id)
  }

  return (
    <div className="flex items-center gap-1 h-full">
      <button
        onClick={handleEditar}
        className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-black hover:text-black hover:bg-gray-100 transition-colors cursor-pointer"
        title="Editar lançamento"
      >
        <IconPencil />
        Editar
      </button>

      {lancamento.ativo && lancamento.status === 'PENDENTE' && (
        <button
          onClick={handleMarcarPago}
          disabled={isBusy}
          className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-gray-600 hover:text-black hover:bg-gray-100 transition-colors disabled:opacity-50 cursor-pointer"
          title="Marcar como pago"
        >
          <IconCheck />
          Pago
        </button>
      )}

      {lancamento.ativo ? (
        <button
          onClick={handleArquivar}
          disabled={isBusy}
          className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-gray-600 hover:text-black hover:bg-gray-100 transition-colors disabled:opacity-50 cursor-pointer"
          title="Arquivar lançamento"
        >
          <IconArchive />
          Arquivar
        </button>
      ) : (
        <button
          onClick={handleRestaurar}
          disabled={isBusy}
          className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-gray-600 hover:text-black hover:bg-gray-100 transition-colors disabled:opacity-50 cursor-pointer"
          title="Restaurar lançamento"
        >
          <IconUndo />
          Restaurar
        </button>
      )}
    </div>
  )
}

function IconPencil() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
    </svg>
  )
}

function IconArchive() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="5" />
      <path d="M4 8v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8" />
      <path d="M10 12h4" />
    </svg>
  )
}

function IconCheck() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 6 9 17l-5-5" />
    </svg>
  )
}

function IconUndo() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 7v6h6" />
      <path d="M21 17a9 9 0 0 0-15-6.7L3 13" />
    </svg>
  )
}
