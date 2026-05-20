import { useFormContext, useWatch } from 'react-hook-form'

import type { ProdutoEditorForm } from './schema'
import { formatPercent } from '../../utils/format'

interface Props {
  index: number
  onRemove: () => void
  canRemove: boolean
}

export function VariacaoCard({ index, onRemove, canRemove }: Props) {
  const {
    register,
    control,
    formState: { errors },
  } = useFormContext<ProdutoEditorForm>()

  const custo = useWatch({ control, name: `variacoes.${index}.custo` })
  const precoSite = useWatch({
    control,
    name: `variacoes.${index}.preco_site`,
  })
  const sku = useWatch({ control, name: `variacoes.${index}.sku_nuvemshop` })
  const descricao = useWatch({
    control,
    name: `variacoes.${index}.descricao`,
  })

  const margem = (() => {
    const c = parseFloat(custo || '0')
    const p = parseFloat(precoSite || '0')
    if (!c || c === 0 || !precoSite) return null
    return ((p - c) / c) * 100
  })()

  const varErrors = errors.variacoes?.[index]

  return (
    <div className="border border-gray-200 bg-white p-5">
      <div className="flex items-start justify-between mb-4 gap-4">
        <div className="min-w-0">
          <div className="kicker mb-1">Variação · #{index + 1}</div>
          {(sku || descricao) && (
            <p className="text-sm text-black truncate">
              {sku && <span className="font-mono">{sku}</span>}
              {sku && descricao && (
                <span className="text-gray-400 mx-2">·</span>
              )}
              {descricao && <span>{descricao}</span>}
            </p>
          )}
        </div>
        {canRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="inline-flex items-center gap-1.5 px-2 py-1 text-xs text-gray-600 hover:text-orange-dark hover:bg-orange-soft transition-colors shrink-0"
            title="Remover variação"
          >
            <IconTrash />
            Remover
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Field label="SKU NuvemShop">
          <input
            type="text"
            {...register(`variacoes.${index}.sku_nuvemshop`)}
            className="form-input font-mono"
          />
        </Field>

        <Field label="ID GestãoClick">
          <input
            type="text"
            {...register(`variacoes.${index}.id_gestaoclick`)}
            className="form-input font-mono"
          />
        </Field>

        <Field label="Variação (cor, tipo)">
          <input
            type="text"
            {...register(`variacoes.${index}.descricao`)}
            className="form-input"
          />
        </Field>

        <Field label="Custo" required>
          <input
            type="number"
            step="0.01"
            {...register(`variacoes.${index}.custo`)}
            className="form-input font-mono"
          />
          {varErrors?.custo && (
            <FieldError>{varErrors.custo.message}</FieldError>
          )}
        </Field>

        <Field label="Preço Loja" required>
          <input
            type="number"
            step="0.01"
            {...register(`variacoes.${index}.preco_loja`)}
            className="form-input font-mono"
          />
          {varErrors?.preco_loja && (
            <FieldError>{varErrors.preco_loja.message}</FieldError>
          )}
        </Field>

        <Field label="Preço Site (opcional)">
          <input
            type="number"
            step="0.01"
            {...register(`variacoes.${index}.preco_site`)}
            className="form-input font-mono"
            placeholder="—"
          />
        </Field>

        <Field label="Margem %">
          <div className="form-input bg-gray-50 cursor-not-allowed text-gray-600 flex items-center font-mono">
            {margem === null ? (
              <span className="text-gray-400">—</span>
            ) : (
              <span>{formatPercent(margem)}</span>
            )}
          </div>
        </Field>

        <Field label="Status NuvemShop">
          <select
            {...register(`variacoes.${index}.status_nuvemshop`)}
            className="form-input"
          >
            <option value="ATIVO">Ativo</option>
            <option value="INATIVO">Inativo</option>
          </select>
        </Field>

        <Field label="Status Integração">
          <select
            {...register(`variacoes.${index}.status_integracao`)}
            className="form-input"
          >
            <option value="ATIVO">Ativo</option>
            <option value="INATIVO">Inativo</option>
          </select>
        </Field>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100">
        <label className="inline-flex items-center gap-2 text-sm text-black select-none cursor-pointer">
          <input
            type="checkbox"
            {...register(`variacoes.${index}.ativo`)}
            className="accent-orange"
          />
          Variação ativa
        </label>
      </div>
    </div>
  )
}

function Field({
  label,
  required,
  children,
}: {
  label: string
  required?: boolean
  children: React.ReactNode
}) {
  return (
    <div>
      <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
        {label}
        {required && <span className="text-orange ml-1">*</span>}
      </label>
      {children}
    </div>
  )
}

function FieldError({ children }: { children: React.ReactNode }) {
  return <p className="mt-1 text-xs text-orange-dark">{children}</p>
}

function IconTrash() {
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
      <path d="M3 6h18" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
      <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  )
}
