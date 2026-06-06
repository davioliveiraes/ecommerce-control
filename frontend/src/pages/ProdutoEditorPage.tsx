import { useEffect } from 'react'
import { useParams, useNavigate, Navigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm, useFieldArray, FormProvider } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'

import { fetchProduto, saveProdutoComVariacoes } from '../api/produtos'
import { fetchVariacoesPorProduto } from '../api/variacoes'
import { fetchMarcas } from '../api/marcas'
import { fetchSubcategorias } from '../api/subcategorias'
import {
  produtoEditorSchema,
  type ProdutoEditorForm,
} from '../components/produto-editor/schema'
import { ProdutoSection } from '../components/produto-editor/ProdutoSection'
import { VariacaoCard } from '../components/produto-editor/VariacaoCard'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { useUnsavedChangesWarning } from '../hooks/useUnsavedChangesWarning'

export function ProdutoEditorPage() {
  useDocumentTitle('Editar produto — {{COMPANY_NAME}} Catálogo')

  const { id } = useParams<{ id: string }>()
  const produtoId = Number(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const isValidId = produtoId && !isNaN(produtoId)

  const produtoQuery = useQuery({
    queryKey: ['produto', produtoId],
    queryFn: () => fetchProduto(produtoId),
    enabled: !!isValidId,
  })

  const variacoesQuery = useQuery({
    queryKey: ['variacoes-do-produto', produtoId],
    queryFn: () => fetchVariacoesPorProduto(produtoId),
    enabled: !!isValidId,
  })

  const marcasQuery = useQuery({ queryKey: ['marcas'], queryFn: fetchMarcas })
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
      marca_id: null,
      subcategoria_id: null,
      variacoes: [],
    },
  })

  const { control, handleSubmit, reset, formState } = methods
  const { fields, append, remove } = useFieldArray({
    control,
    name: 'variacoes',
  })

  useEffect(() => {
    if (produtoQuery.data && variacoesQuery.data) {
      reset({
        nome_gestaoclick: produtoQuery.data.nome_gestaoclick,
        nome_site: produtoQuery.data.nome_site,
        descricao_produto_gestaoclick:
          produtoQuery.data.descricao_produto_gestaoclick,
        descricao_produto_site: produtoQuery.data.descricao_produto_site,
        marca_id: produtoQuery.data.marca_id,
        subcategoria_id: produtoQuery.data.subcategoria_id,
        variacoes: variacoesQuery.data.map((v) => ({
          id: v.id,
          sku_nuvemshop: v.sku_nuvemshop,
          id_gestaoclick: v.id_gestaoclick,
          codigo_barras: v.codigo_barras,
          descricao: v.descricao,
          custo: v.custo,
          preco_loja: v.preco_loja,
          preco_site: v.preco_site,
          preco_promocional: v.preco_promocional,
          status_nuvemshop: v.status_nuvemshop,
          status_integracao: v.status_integracao,
          ativo: v.ativo,
        })),
      })
    }
  }, [produtoQuery.data, variacoesQuery.data, reset])

  useUnsavedChangesWarning(formState.isDirty)

  const saveMutation = useMutation({
    mutationFn: (data: ProdutoEditorForm) =>
      saveProdutoComVariacoes(produtoId, {
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
      queryClient.invalidateQueries({ queryKey: ['produto', produtoId] })
      queryClient.invalidateQueries({
        queryKey: ['variacoes-do-produto', produtoId],
      })
      navigate('/catalogo')
    },
  })

  const onSubmit = (data: ProdutoEditorForm) => {
    saveMutation.mutate(data)
  }

  if (!isValidId) {
    return <Navigate to="/catalogo" replace />
  }

  if (produtoQuery.isLoading || variacoesQuery.isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-16 text-center font-mono text-sm text-gray-600">
        carregando produto...
      </div>
    )
  }

  if (produtoQuery.isError || variacoesQuery.isError) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-12">
        <div className="border border-gray-300 bg-gray-50 px-6 py-5">
          <div className="kicker mb-2">Erro</div>
          <h3 className="font-display text-lg font-semibold text-black mb-1">
            Falha ao carregar produto
          </h3>
          <p className="text-sm text-gray-600">
            Verifique se o produto ainda existe ou se a API está acessível.
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
              onClick={() => navigate('/catalogo')}
              className="inline-flex items-center gap-1.5 text-xs text-gray-600 hover:text-black transition-colors mb-3 font-mono"
            >
              <IconArrowLeft />
              voltar ao catálogo
            </button>
            <div className="kicker mb-2">Módulo 01 · Edição</div>
            <h1 className="font-display text-3xl font-semibold text-black tracking-tight mb-1">
              Editar produto — {`{{COMPANY_NAME}}`} Catálogo
            </h1>
            <p className="text-sm text-gray-600 truncate">
              {produtoQuery.data?.descricao_produto_site}
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              type="button"
              onClick={() => navigate('/catalogo')}
              className="px-4 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saveMutation.isPending || !formState.isDirty}
              className="px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {saveMutation.isPending ? 'salvando...' : 'Salvar alterações'}
            </button>
          </div>
        </div>

        {saveMutation.isError && (
          <div className="border border-gray-300 bg-gray-50 px-4 py-3 mb-6">
            <div className="kicker mb-1">Erro</div>
            <p className="text-sm text-black">
              Falha ao salvar:{' '}
              {(saveMutation.error as Error)?.message || 'erro desconhecido'}
            </p>
          </div>
        )}

        <ProdutoSection
          marcas={marcasQuery.data || []}
          subcategorias={subcategoriasQuery.data || []}
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
              onClick={() =>
                append({
                  sku_nuvemshop: '',
                  id_gestaoclick: '',
                  codigo_barras: '',
                  descricao: '',
                  custo: '0',
                  preco_loja: '0',
                  preco_site: null,
                  preco_promocional: null,
                  status_nuvemshop: 'ATIVO',
                  status_integracao: 'ATIVO',
                  ativo: true,
                })
              }
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
