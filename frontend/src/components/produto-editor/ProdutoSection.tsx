import { useEffect, useState } from 'react'
import { useFormContext } from 'react-hook-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { isAxiosError } from 'axios'

import { createCategoria } from '../../api/categorias'
import { createSubcategoria } from '../../api/subcategorias'
import type { ProdutoEditorForm } from './schema'
import type { Categoria, Subcategoria } from '../../types/catalog'

interface Props {
  categorias: Categoria[]
  subcategorias: Subcategoria[]
  permitirCriar?: boolean
}

function mensagemDeErro(error: unknown): string {
  if (isAxiosError(error)) {
    return error.response?.data?.detail || error.message
  }
  return 'erro desconhecido'
}

export function ProdutoSection({
  categorias,
  subcategorias,
  permitirCriar = false,
}: Props) {
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = useFormContext<ProdutoEditorForm>()

  const queryClient = useQueryClient()
  const [criando, setCriando] = useState<'categoria' | 'subcategoria' | null>(
    null,
  )

  const categoriaId = watch('categoria_id')
  const subcategoriaId = watch('subcategoria_id')

  // Subcategoria é opcional e sempre subordinada à categoria escolhida.
  const subcategoriasDaCategoria =
    categoriaId === null
      ? subcategorias
      : subcategorias.filter((s) => s.categoria_id === categoriaId)

  // Se a categoria mudar e a subcategoria atual não pertencer a ela, limpa.
  useEffect(() => {
    if (
      subcategoriaId !== null &&
      categoriaId !== null &&
      !subcategorias.some(
        (s) => s.id === subcategoriaId && s.categoria_id === categoriaId,
      )
    ) {
      setValue('subcategoria_id', null, { shouldDirty: true })
    }
  }, [categoriaId, subcategoriaId, subcategorias, setValue])

  const criarCategoriaMutation = useMutation({
    mutationFn: createCategoria,
    onSuccess: (categoria) => {
      // Injeta no cache antes do setValue para o select já ter a opção.
      queryClient.setQueryData<Categoria[]>(['categorias'], (atuais) =>
        atuais && !atuais.some((c) => c.id === categoria.id)
          ? [...atuais, categoria].sort((a, b) => a.nome.localeCompare(b.nome))
          : atuais,
      )
      queryClient.invalidateQueries({ queryKey: ['categorias'] })
      setValue('categoria_id', categoria.id, { shouldDirty: true })
      setCriando(null)
    },
  })

  const criarSubcategoriaMutation = useMutation({
    mutationFn: (nome: string) => {
      if (categoriaId === null) {
        return Promise.reject(new Error('Selecione uma categoria primeiro.'))
      }
      return createSubcategoria(nome, categoriaId)
    },
    onSuccess: (subcategoria) => {
      queryClient.setQueryData<Subcategoria[]>(['subcategorias'], (atuais) =>
        atuais && !atuais.some((s) => s.id === subcategoria.id)
          ? [...atuais, subcategoria]
          : atuais,
      )
      queryClient.invalidateQueries({ queryKey: ['subcategorias'] })
      setValue('subcategoria_id', subcategoria.id, { shouldDirty: true })
      setCriando(null)
    },
  })

  return (
    <section className="border border-gray-200 bg-white p-6">
      <div className="kicker mb-1">Identidade</div>
      <h2 className="font-display text-xl font-semibold text-black mb-5">
        Produto
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <FieldLabel required>Descrição (NuvemShop)</FieldLabel>
          <textarea
            {...register('descricao_produto_site')}
            rows={3}
            className="form-input"
          />
          {errors.descricao_produto_site && (
            <FieldError>{errors.descricao_produto_site.message}</FieldError>
          )}
        </div>

        <div className="md:col-span-2">
          <FieldLabel>Descrição (GestãoClick)</FieldLabel>
          <textarea
            {...register('descricao_produto_gestaoclick')}
            rows={3}
            className="form-input"
          />
        </div>

        <div>
          <div className="flex items-baseline justify-between">
            <FieldLabel>Categoria</FieldLabel>
            {permitirCriar && criando !== 'categoria' && (
              <BotaoCriar onClick={() => setCriando('categoria')}>
                + criar categoria
              </BotaoCriar>
            )}
          </div>
          <select
            {...register('categoria_id', {
              setValueAs: (v) =>
                v === '' || v === null ? null : Number(v),
            })}
            className="form-input"
          >
            <option value="">— Sem categoria —</option>
            {categorias.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome}
              </option>
            ))}
          </select>
          {criando === 'categoria' && (
            <CriarInline
              placeholder="Nome da nova categoria"
              isPending={criarCategoriaMutation.isPending}
              erro={
                criarCategoriaMutation.isError
                  ? mensagemDeErro(criarCategoriaMutation.error)
                  : null
              }
              onConfirm={(nome) => criarCategoriaMutation.mutate(nome)}
              onCancel={() => {
                criarCategoriaMutation.reset()
                setCriando(null)
              }}
            />
          )}
        </div>

        <div>
          <div className="flex items-baseline justify-between">
            <FieldLabel>Subcategoria</FieldLabel>
            {permitirCriar &&
              criando !== 'subcategoria' &&
              categoriaId !== null && (
                <BotaoCriar onClick={() => setCriando('subcategoria')}>
                  + criar subcategoria
                </BotaoCriar>
              )}
          </div>
          <select
            {...register('subcategoria_id', {
              setValueAs: (v) =>
                v === '' || v === null ? null : Number(v),
            })}
            className="form-input"
          >
            <option value="">— Sem subcategoria —</option>
            {subcategoriasDaCategoria.map((s) => (
              <option key={s.id} value={s.id}>
                {categoriaId === null ? `${s.categoria_nome} › ${s.nome}` : s.nome}
              </option>
            ))}
          </select>
          {permitirCriar && categoriaId === null && (
            <p className="mt-1 text-xs text-gray-500">
              Selecione uma categoria para poder criar subcategorias.
            </p>
          )}
          {criando === 'subcategoria' && (
            <CriarInline
              placeholder="Nome da nova subcategoria"
              isPending={criarSubcategoriaMutation.isPending}
              erro={
                criarSubcategoriaMutation.isError
                  ? mensagemDeErro(criarSubcategoriaMutation.error)
                  : null
              }
              onConfirm={(nome) => criarSubcategoriaMutation.mutate(nome)}
              onCancel={() => {
                criarSubcategoriaMutation.reset()
                setCriando(null)
              }}
            />
          )}
        </div>
      </div>
    </section>
  )
}

function BotaoCriar({
  children,
  onClick,
}: {
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="font-mono text-xs text-gray-600 hover:text-black transition-colors mb-1.5"
    >
      {children}
    </button>
  )
}

function CriarInline({
  placeholder,
  isPending,
  erro,
  onConfirm,
  onCancel,
}: {
  placeholder: string
  isPending: boolean
  erro: string | null
  onConfirm: (nome: string) => void
  onCancel: () => void
}) {
  const [nome, setNome] = useState('')

  const confirmar = () => {
    const limpo = nome.trim()
    if (limpo) onConfirm(limpo)
  }

  return (
    <div className="mt-2">
      <div className="flex items-center gap-2">
        <input
          autoFocus
          value={nome}
          onChange={(e) => setNome(e.target.value)}
          onKeyDown={(e) => {
            // Enter confirma a criação sem submeter o form do produto.
            if (e.key === 'Enter') {
              e.preventDefault()
              confirmar()
            }
            if (e.key === 'Escape') onCancel()
          }}
          placeholder={placeholder}
          className="form-input"
        />
        <button
          type="button"
          onClick={confirmar}
          disabled={isPending || !nome.trim()}
          className="px-3 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
        >
          {isPending ? 'criando...' : 'Criar'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors shrink-0"
        >
          Cancelar
        </button>
      </div>
      {erro && <FieldError>{erro}</FieldError>}
    </div>
  )
}

function FieldLabel({
  children,
  required,
}: {
  children: React.ReactNode
  required?: boolean
}) {
  return (
    <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
      {children}
      {required && <span className="text-black ml-1">*</span>}
    </label>
  )
}

function FieldError({ children }: { children: React.ReactNode }) {
  return <p className="mt-1 text-xs text-gray-900">{children}</p>
}
