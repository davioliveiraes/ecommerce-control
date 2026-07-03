import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'

import type {
  VisaoGeralPeriodo,
  VisaoGeralPeriodoInput,
} from '../../types/visaoGeral'

const inteiro = z
  .number({ error: 'Informe um número' })
  .int('Use um número inteiro')
  .min(0, 'Não pode ser negativo')

const schema = z
  .object({
    data_inicio: z.string().min(1, 'Informe a data inicial'),
    data_fim: z.string().min(1, 'Informe a data final'),
    visitas: inteiro,
    visualizacoes_categoria: inteiro,
    visualizacoes_produto: inteiro,
    carrinhos_criados: inteiro,
    checkout_iniciado: inteiro,
    checkout_entrega: inteiro,
    checkout_pagamento: inteiro,
    pedidos_criados: inteiro,
    pedidos_pagos: inteiro,
    receita: z
      .number({ error: 'Informe um valor' })
      .min(0, 'Não pode ser negativo'),
    observacao: z.string().max(1000),
  })
  .refine((v) => v.data_inicio <= v.data_fim, {
    message: 'A data inicial deve ser anterior ou igual à final',
    path: ['data_fim'],
  })

type FormValues = z.infer<typeof schema>

const EMPTY: FormValues = {
  data_inicio: '',
  data_fim: '',
  visitas: 0,
  visualizacoes_categoria: 0,
  visualizacoes_produto: 0,
  carrinhos_criados: 0,
  checkout_iniciado: 0,
  checkout_entrega: 0,
  checkout_pagamento: 0,
  pedidos_criados: 0,
  pedidos_pagos: 0,
  receita: 0,
  observacao: '',
}

function fromPeriodo(p: VisaoGeralPeriodo): FormValues {
  return {
    data_inicio: p.data_inicio,
    data_fim: p.data_fim,
    visitas: p.visitas,
    visualizacoes_categoria: p.visualizacoes_categoria,
    visualizacoes_produto: p.visualizacoes_produto,
    carrinhos_criados: p.carrinhos_criados,
    checkout_iniciado: p.checkout_iniciado,
    checkout_entrega: p.checkout_entrega,
    checkout_pagamento: p.checkout_pagamento,
    pedidos_criados: p.pedidos_criados,
    pedidos_pagos: p.pedidos_pagos,
    receita: parseFloat(p.receita) || 0,
    observacao: p.observacao,
  }
}

interface Props {
  open: boolean
  editing: VisaoGeralPeriodo | null
  isSubmitting: boolean
  error: string | null
  onClose: () => void
  onSubmit: (payload: VisaoGeralPeriodoInput) => void
}

export function VisaoGeralPeriodoForm({
  open,
  editing,
  isSubmitting,
  error,
  onClose,
  onSubmit,
}: Props) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: EMPTY,
  })

  useEffect(() => {
    if (!open) return
    reset(editing ? fromPeriodo(editing) : EMPTY)
  }, [open, editing, reset])

  if (!open) return null

  const submit = handleSubmit((values) => {
    onSubmit(values)
  })

  // Overlay em preto literal: bg-black remapeia para claro no tema dark
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#000]/45 p-4">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-200 bg-white shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-gray-200 px-6 py-4">
          <div>
            <div className="kicker mb-1">Visão geral — controle interno</div>
            <h2 className="font-display text-xl font-semibold text-black">
              {editing ? 'Editar período' : 'Adicionar período'}
            </h2>
            <p className="mt-1 text-xs text-gray-600">
              Preencha com os números do relatório da NuvemShop. Ticket e
              conversões são calculados automaticamente.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={isSubmitting}
            className="inline-flex h-8 w-8 items-center justify-center border border-gray-200 text-gray-600 hover:border-black hover:text-black transition-colors disabled:opacity-50"
            aria-label="Fechar"
          >
            <IconClose />
          </button>
        </div>

        <form onSubmit={submit} className="px-6 py-4">
          <div className="grid grid-cols-2 gap-4">
            <DateField
              label="Início do período"
              error={errors.data_inicio?.message}
              {...register('data_inicio')}
            />
            <DateField
              label="Fim do período"
              error={errors.data_fim?.message}
              {...register('data_fim')}
            />
          </div>

          <Section title="Tráfego e visitantes">
            <NumberField
              label="Visitas"
              error={errors.visitas?.message}
              {...register('visitas', { valueAsNumber: true })}
            />
            <NumberField
              label="Visualizações de categoria"
              error={errors.visualizacoes_categoria?.message}
              {...register('visualizacoes_categoria', { valueAsNumber: true })}
            />
            <NumberField
              label="Visualizações de produto"
              error={errors.visualizacoes_produto?.message}
              {...register('visualizacoes_produto', { valueAsNumber: true })}
            />
            <NumberField
              label="Carrinhos criados"
              error={errors.carrinhos_criados?.message}
              {...register('carrinhos_criados', { valueAsNumber: true })}
            />
          </Section>

          <Section title="Funil de checkout">
            <NumberField
              label="Checkout iniciado"
              error={errors.checkout_iniciado?.message}
              {...register('checkout_iniciado', { valueAsNumber: true })}
            />
            <NumberField
              label="Etapa de entrega"
              error={errors.checkout_entrega?.message}
              {...register('checkout_entrega', { valueAsNumber: true })}
            />
            <NumberField
              label="Etapa de pagamento"
              error={errors.checkout_pagamento?.message}
              {...register('checkout_pagamento', { valueAsNumber: true })}
            />
            <NumberField
              label="Pedidos criados"
              error={errors.pedidos_criados?.message}
              {...register('pedidos_criados', { valueAsNumber: true })}
            />
            <NumberField
              label="Pedidos pagos (vendas)"
              error={errors.pedidos_pagos?.message}
              {...register('pedidos_pagos', { valueAsNumber: true })}
            />
            <NumberField
              label="Receita (R$)"
              step="0.01"
              error={errors.receita?.message}
              {...register('receita', { valueAsNumber: true })}
            />
          </Section>

          <div className="mt-4">
            <label className="mb-1 block text-xs font-medium text-gray-700">
              Observação
            </label>
            <textarea
              rows={2}
              {...register('observacao')}
              className="w-full border border-gray-200 bg-white px-3 py-2 text-sm text-black focus:border-black focus:outline-none"
              placeholder="Opcional — ex.: origem do relatório, campanha do período..."
            />
          </div>

          {error && (
            <p className="mt-3 border border-black bg-gray-50 px-3 py-2 text-sm text-black">
              {error}
            </p>
          )}

          <div className="mt-5 flex justify-end gap-2 border-t border-gray-200 pt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 hover:border-black hover:text-black transition-colors disabled:opacity-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="border border-black bg-black px-4 py-2 text-sm text-white hover:bg-gray-900 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Salvando...' : 'Salvar período'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function Section({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <fieldset className="mt-5">
      <legend className="mb-2 font-mono text-[10px] uppercase tracking-wider text-gray-500">
        {title}
      </legend>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">{children}</div>
    </fieldset>
  )
}

const NumberField = ({
  label,
  error,
  step,
  ref,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string
  error?: string
  ref?: React.Ref<HTMLInputElement>
}) => (
  <div>
    <label className="mb-1 block text-xs font-medium text-gray-700">
      {label}
    </label>
    <input
      ref={ref}
      type="number"
      step={step ?? '1'}
      min="0"
      {...props}
      className="w-full border border-gray-200 bg-white px-3 py-2 font-mono text-sm tabular-nums text-black focus:border-black focus:outline-none"
    />
    {error && <p className="mt-1 text-[11px] text-black">{error}</p>}
  </div>
)

const DateField = ({
  label,
  error,
  ref,
  ...props
}: React.InputHTMLAttributes<HTMLInputElement> & {
  label: string
  error?: string
  ref?: React.Ref<HTMLInputElement>
}) => (
  <div>
    <label className="mb-1 block text-xs font-medium text-gray-700">
      {label}
    </label>
    <input
      ref={ref}
      type="date"
      {...props}
      className="w-full border border-gray-200 bg-white px-3 py-2 text-sm text-black focus:border-black focus:outline-none"
    />
    {error && <p className="mt-1 text-[11px] text-black">{error}</p>}
  </div>
)

function IconClose() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  )
}
