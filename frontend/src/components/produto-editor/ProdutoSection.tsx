import { useFormContext } from 'react-hook-form'

import type { ProdutoEditorForm } from './schema'
import type { Marca, Subcategoria } from '../../types/catalog'

interface Props {
  marcas: Marca[]
  subcategorias: Subcategoria[]
}

export function ProdutoSection({ marcas, subcategorias }: Props) {
  const {
    register,
    formState: { errors },
  } = useFormContext<ProdutoEditorForm>()

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
          <FieldLabel>Marca</FieldLabel>
          <select
            {...register('marca_id', {
              setValueAs: (v) =>
                v === '' || v === null ? null : Number(v),
            })}
            className="form-input"
          >
            <option value="">— Sem marca —</option>
            {marcas.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nome}
              </option>
            ))}
          </select>
        </div>

        <div>
          <FieldLabel>Subcategoria</FieldLabel>
          <select
            {...register('subcategoria_id', {
              setValueAs: (v) =>
                v === '' || v === null ? null : Number(v),
            })}
            className="form-input"
          >
            <option value="">— Sem subcategoria —</option>
            {subcategorias.map((s) => (
              <option key={s.id} value={s.id}>
                {s.categoria_nome} › {s.nome}
              </option>
            ))}
          </select>
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
      {required && <span className="text-black ml-1">*</span>}
    </label>
  )
}

function FieldError({ children }: { children: React.ReactNode }) {
  return <p className="mt-1 text-xs text-gray-900">{children}</p>
}
