import { useFormContext, useWatch } from 'react-hook-form'

import type { LancamentoFinanceiroForm } from './schema'
import type { CategoriaFinanceira } from '../../types/finance'
import { formatCurrency } from '../../utils/format'

interface Props {
  categorias: CategoriaFinanceira[]
}

export function LancamentoFinanceiroSection({ categorias }: Props) {
  const {
    register,
    control,
    formState: { errors },
  } = useFormContext<LancamentoFinanceiroForm>()

  const tipo = useWatch({ control, name: 'tipo' })
  const valor = useWatch({ control, name: 'valor' })

  const natureza = tipo === 'RECEITA' ? 'Entrada' : 'Saída'
  const previewValue = formatCurrency(valor || null)

  return (
    <section className="border border-gray-200 bg-white p-6">
      <div className="flex items-start justify-between gap-6 mb-5">
        <div>
          <div className="kicker mb-1">Detalhes</div>
          <h2 className="font-display text-xl font-semibold text-black">
            Lançamento
          </h2>
        </div>

        <div className="text-right shrink-0">
          <div className="font-mono text-xs uppercase tracking-wider text-gray-600 mb-1">
            {natureza}
          </div>
          <div
            className={`font-mono text-lg tabular-nums ${
              tipo === 'RECEITA' ? 'text-navy' : 'text-orange-dark'
            }`}
          >
            {previewValue}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <FieldLabel required>Descrição</FieldLabel>
          <input type="text" {...register('descricao')} className="form-input" />
          {errors.descricao && (
            <FieldError>{errors.descricao.message}</FieldError>
          )}
        </div>

        <div>
          <FieldLabel required>Tipo</FieldLabel>
          <select {...register('tipo')} className="form-input">
            <option value="RECEITA">Receita · entrada</option>
            <option value="DESPESA">Despesa · saída</option>
            <option value="CUSTO">Custo · saída</option>
          </select>
        </div>

        <div>
          <FieldLabel>Categoria</FieldLabel>
          <select
            {...register('categoria_id', {
              setValueAs: (value) =>
                value === '' || value === null ? null : Number(value),
            })}
            className="form-input"
          >
            <option value="">— Sem categoria —</option>
            {categorias.map((categoria) => (
              <option key={categoria.id} value={categoria.id}>
                {categoria.nome}
              </option>
            ))}
          </select>
        </div>

        <div>
          <FieldLabel required>Valor</FieldLabel>
          <input
            type="number"
            step="0.01"
            min="0.01"
            {...register('valor')}
            className="form-input font-mono"
          />
          {errors.valor && <FieldError>{errors.valor.message}</FieldError>}
        </div>

        <div>
          <FieldLabel required>Data de vencimento</FieldLabel>
          <input
            type="date"
            {...register('data_lancamento')}
            className="form-input font-mono"
          />
          {errors.data_lancamento && (
            <FieldError>{errors.data_lancamento.message}</FieldError>
          )}
        </div>

        <div>
          <FieldLabel>Status</FieldLabel>
          <select {...register('status')} className="form-input">
            <option value="PENDENTE">Pendente</option>
            <option value="PAGO">Pago</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <FieldLabel>Observações</FieldLabel>
          <textarea
            {...register('observacoes')}
            rows={4}
            className="form-input"
          />
        </div>
      </div>
    </section>
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
      {required && <span className="text-orange ml-1">*</span>}
    </label>
  )
}

function FieldError({ children }: { children: React.ReactNode }) {
  return <p className="mt-1 text-xs text-orange-dark">{children}</p>
}
