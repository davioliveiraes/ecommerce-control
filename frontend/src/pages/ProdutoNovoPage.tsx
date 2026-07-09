import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, useFieldArray, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

import { createProdutoComVariacoes } from '../api/produtos'
import { fetchCategorias } from '../api/categorias'
import { fetchSubcategorias } from '../api/subcategorias'
import {
  produtoEditorSchema,
  type ProdutoEditorForm,
} from '../components/produto-editor/schema'
import { ProdutoSection } from '../components/produto-editor/ProdutoSection'
import { VariacaoCard } from '../components/produto-editor/VariacaoCard'
import { ConfirmDialog } from '../components/ConfirmDialog'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useUnsavedChangesWarning } from '../hooks/useUnsavedChangesWarning'

const variacaoVazia = {
  sku_nuvemshop: '',
  id_gestaoclick: '',
  codigo_barras: '',
  descricao: '',
  custo: '0',
  preco_loja: '0',
  preco_site: null,
  preco_promocional: null,
  status_nuvemshop: 'ATIVO' as const,
  status_integracao: 'ATIVO' as const,
  ativo: true,
}

export function ProdutoNovoPage() {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''

  useDocumentTitle(`Adicionar produto — ${nomeEmpresa} Catálogo`)

  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const categoriasQuery = useQuery({
    queryKey: ['categorias'],
    queryFn: fetchCategorias,
  })
  const subcategoriasQuery = useQuery({
    queryKey: ['subcategorias'],
    queryFn: fetchSubcategorias,
  })

  const methods = useForm<ProdutoEditorForm>({
    resolver: zodResolver(produtoEditorSchema),
    defaultValues: {
      nome_gestaoclick: '',
      nome_site: '',
      descricao_produto_gestaoclick: '',
      descricao_produto_site: '',
      categoria_id: null,
      subcategoria_id: null,
      variacoes: [variacaoVazia],
    },
  })

  const { control, handleSubmit, formState } = methods
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'variacoes',
  })

  const { dialog: unsavedDialog, allowNavigation } = useUnsavedChangesWarning(
    formState.isDirty && !formState.isSubmitSuccessful,
  )

  const [dialog, setDialog] = useState<'save' | 'cancel' | null>(null)
  const pendingData = useRef<ProdutoEditorForm | null>(null)

  const createMutation = useMutation({
    mutationFn: (data: ProdutoEditorForm) =>
      createProdutoComVariacoes({
        ...data,
        variacoes: data.variacoes.map((v) => ({
          ...v,
          preco_site: v.preco_site === '' ? null : v.preco_site,
          preco_promocional:
            v.preco_promocional === '' ? null : v.preco_promocional,
        })),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variacoes'] })
      allowNavigation()
      navigate('/catalogo')
    },
    onError: () => {
      setDialog(null)
    },
  })

  // Só chega aqui se o form for válido; guardamos e confirmamos antes de criar.
  const onSubmit = (data: ProdutoEditorForm) => {
    pendingData.current = data
    setDialog('save')
  }

  const handleConfirmSave = () => {
    if (pendingData.current) createMutation.mutate(pendingData.current)
  }

  const handleCancel = () => {
    if (formState.isDirty) {
      setDialog('cancel')
    } else {
      navigate('/catalogo')
    }
  }

  const handleConfirmDiscard = () => {
    allowNavigation()
    navigate('/catalogo')
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
              onClick={() => navigate('/catalogo')}
              className="inline-flex items-center gap-1.5 text-xs text-gray-600 hover:text-black transition-colors mb-3 font-mono"
            >
              <IconArrowLeft />
              voltar ao catálogo
            </button>
            <div className="kicker mb-2">Módulo 01 · Novo produto</div>
            <h1 className="font-display text-3xl font-semibold text-black tracking-tight mb-1">
              Adicionar produto — {nomeEmpresa} Catálogo
            </h1>
            <p className="text-sm text-gray-600">
              Cadastre o produto e ao menos uma variação com custo e preços.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {createMutation.isPending ? 'salvando...' : 'Salvar produto'}
            </button>
          </div>
        </div>

        {createMutation.isError && (
          <div className="border border-gray-300 bg-gray-50 px-4 py-3 mb-6">
            <div className="kicker mb-1">Erro</div>
            <p className="text-sm text-black">
              Falha ao salvar:{' '}
              {(createMutation.error as Error)?.message || 'erro desconhecido'}
            </p>
          </div>
        )}

        <ProdutoSection
          categorias={categoriasQuery.data || []}
          subcategorias={subcategoriasQuery.data || []}
          permitirCriar
        />

        <div className="mt-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="kicker mb-1">Variações</div>
              <h2 className="font-display text-xl font-semibold text-black">
                {fields.length}{' '}
                {fields.length === 1 ? 'variação' : 'variações'}
              </h2>
            </div>
            <button
              type="button"
              onClick={() => append(variacaoVazia)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm border border-black text-black hover:bg-gray-50 transition-colors"
            >
              <IconPlus />
              Adicionar variação
            </button>
          </div>

          <div className="space-y-3">
            {fields.map((field, index) => (
              <VariacaoCard
                key={field.id}
                index={index}
                onRemove={() => remove(index)}
                canRemove={fields.length > 1}
              />
            ))}
          </div>

          {formState.errors.variacoes?.message && (
            <p className="mt-3 text-sm text-gray-900">
              {formState.errors.variacoes.message}
            </p>
          )}
        </div>
      </form>

      <ConfirmDialog
        isOpen={dialog === 'save'}
        title="Adicionar produto?"
        description={
          <>
            O produto{' '}
            <strong className="text-black">
              {pendingData.current?.descricao_produto_site}
            </strong>{' '}
            será criado com{' '}
            {pendingData.current?.variacoes.length ?? fields.length}{' '}
            {(pendingData.current?.variacoes.length ?? fields.length) === 1
              ? 'variação'
              : 'variações'}
            .
          </>
        }
        confirmLabel="Adicionar produto"
        cancelLabel="Voltar"
        isPending={createMutation.isPending}
        onConfirm={handleConfirmSave}
        onCancel={() => setDialog(null)}
      />

      <ConfirmDialog
        isOpen={dialog === 'cancel'}
        title="Descartar produto?"
        description="As informações preenchidas serão perdidas. Esta ação não pode ser desfeita."
        confirmLabel="Descartar"
        cancelLabel="Continuar editando"
        onConfirm={handleConfirmDiscard}
        onCancel={() => setDialog(null)}
      />

      {unsavedDialog}
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

function IconPlus() {
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
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  )
}
