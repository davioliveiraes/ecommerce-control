import { useEffect } from 'react'
import { Navigate, useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { FormProvider, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

import { fetchCategoriasFinanceiras } from '../api/categoriasFinanceiras'
import {
  createLancamentoFinanceiro,
  fetchLancamentoFinanceiro,
  updateLancamentoFinanceiro,
} from '../api/lancamentosFinanceiros'
import { LancamentoFinanceiroSection } from '../components/lancamento-editor/LancamentoFinanceiroSection'
import {
  lancamentoFinanceiroSchema,
  type LancamentoFinanceiroForm,
} from '../components/lancamento-editor/schema'
import { useUnsavedChangesWarning } from '../hooks/useUnsavedChangesWarning'

function getTodayInputValue() {
  const date = new Date()
  date.setMinutes(date.getMinutes() - date.getTimezoneOffset())
  return date.toISOString().slice(0, 10)
}

export function LancamentoFinanceiroEditorPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isNew = !id
  const lancamentoId = Number(id)
  const isValidId = isNew || (lancamentoId && !isNaN(lancamentoId))

  const lancamentoQuery = useQuery({
    queryKey: ['lancamento-financeiro', lancamentoId],
    queryFn: () => fetchLancamentoFinanceiro(lancamentoId),
    enabled: !isNew && !!isValidId,
  })

  const categoriasQuery = useQuery({
    queryKey: ['categorias-financeiras'],
    queryFn: fetchCategoriasFinanceiras,
  })

  const methods = useForm<LancamentoFinanceiroForm>({
    resolver: zodResolver(lancamentoFinanceiroSchema),
    defaultValues: {
      descricao: '',
      tipo: 'DESPESA',
      categoria_id: null,
      valor: '',
      data_lancamento: getTodayInputValue(),
      status: 'PENDENTE',
      forma_pagamento: '',
      meio_pagamento: '',
      quantidade_parcelas: null,
      quantidade_vendas: 1,
      fonte_trafego: '',
      observacoes: '',
    },
  })

  const { handleSubmit, reset, formState } = methods

  useEffect(() => {
    if (lancamentoQuery.data) {
      reset({
        descricao: lancamentoQuery.data.descricao,
        tipo: lancamentoQuery.data.tipo,
        categoria_id: lancamentoQuery.data.categoria_id,
        valor: lancamentoQuery.data.valor,
        data_lancamento: lancamentoQuery.data.data_lancamento,
        status: lancamentoQuery.data.status,
        forma_pagamento: lancamentoQuery.data.forma_pagamento,
        meio_pagamento: lancamentoQuery.data.meio_pagamento,
        quantidade_parcelas: lancamentoQuery.data.quantidade_parcelas,
        quantidade_vendas: lancamentoQuery.data.quantidade_vendas,
        fonte_trafego: lancamentoQuery.data.fonte_trafego,
        observacoes: lancamentoQuery.data.observacoes,
      })
    }
  }, [lancamentoQuery.data, reset])

  useUnsavedChangesWarning(formState.isDirty)

  const saveMutation = useMutation({
    mutationFn: (data: LancamentoFinanceiroForm) =>
      isNew
        ? createLancamentoFinanceiro(data)
        : updateLancamentoFinanceiro(lancamentoId, data),
    onSuccess: (lancamento) => {
      queryClient.invalidateQueries({ queryKey: ['lancamentos-financeiros'] })
      queryClient.invalidateQueries({ queryKey: ['finance-dashboard'] })
      queryClient.invalidateQueries({
        queryKey: ['lancamento-financeiro', lancamento.id],
      })
      navigate('/finance/lancamentos')
    },
  })

  const onSubmit = (data: LancamentoFinanceiroForm) => {
    saveMutation.mutate(data)
  }

  if (!isValidId) {
    return <Navigate to="/finance/lancamentos" replace />
  }

  if (!isNew && lancamentoQuery.isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-16 text-center font-mono text-sm text-gray-600">
        carregando lançamento...
      </div>
    )
  }

  if (!isNew && lancamentoQuery.isError) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="border border-orange/40 bg-orange-soft px-6 py-5">
          <div className="kicker mb-2">Erro</div>
          <h3 className="font-display text-lg font-semibold text-black mb-1">
            Falha ao carregar lançamento
          </h3>
          <p className="text-sm text-gray-600">
            Verifique se o lançamento ainda existe ou se a API está acessível.
          </p>
        </div>
      </div>
    )
  }

  return (
    <FormProvider {...methods}>
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="max-w-5xl mx-auto px-6 py-8"
      >
        <div className="flex items-start justify-between mb-8 gap-6">
          <div className="min-w-0">
            <button
              type="button"
              onClick={() => navigate('/finance/lancamentos')}
              className="inline-flex items-center gap-1.5 text-xs text-gray-600 hover:text-orange transition-colors mb-3 font-mono"
            >
              <IconArrowLeft />
              voltar aos lançamentos
            </button>
            <div className="kicker mb-2">Módulo 02 · Finance</div>
            <h1 className="font-display text-3xl font-semibold text-black tracking-tight mb-1">
              {isNew ? 'Novo lançamento' : 'Editar lançamento'}
            </h1>
            <p className="text-sm text-gray-600 truncate">
              {isNew
                ? 'Cadastre uma entrada ou saída financeira.'
                : lancamentoQuery.data?.descricao}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => navigate('/finance/lancamentos')}
              className="px-4 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending || (!isNew && !formState.isDirty)}
              className="px-4 py-2 text-sm border border-orange bg-orange text-white hover:bg-orange-dark hover:border-orange-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {saveMutation.isPending
                ? 'salvando...'
                : isNew
                  ? 'Criar lançamento'
                  : 'Salvar alterações'}
            </button>
          </div>
        </div>

        {saveMutation.isError && (
          <div className="border border-orange/40 bg-orange-soft px-4 py-3 mb-6">
            <div className="kicker mb-1">Erro</div>
            <p className="text-sm text-black">
              Falha ao salvar:{' '}
              {(saveMutation.error as Error)?.message || 'erro desconhecido'}
            </p>
          </div>
        )}

        <LancamentoFinanceiroSection categorias={categoriasQuery.data || []} />
      </form>
    </FormProvider>
  )
}

function IconArrowLeft() {
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
      <path d="M19 12H5" />
      <path d="m12 19-7-7 7-7" />
    </svg>
  )
}
