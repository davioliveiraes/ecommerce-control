import { MESES_PT } from '../../utils/dateRange'
import type {
  CategoriaFinanceira,
  FinancePeriodoCategoria,
  TipoLancamento,
} from '../../types/finance'

// Mapeia o slug da categoria para o tipo de lançamento correspondente. Quando
// uma categoria específica é escolhida, o tipo fica travado nesse valor.
const CATEGORY_KIND_BY_SLUG: Record<string, TipoLancamento> = {
  'vendas-nuvemshop': 'RECEITA',
  'nuvemshop-plano': 'DESPESA',
  'hospedagem-dominio': 'DESPESA',
  'email-profissional': 'DESPESA',
  'equipe-ecommerce': 'DESPESA',
  'marketing-trafego': 'DESPESA',
  'taxas-meios-pagamento': 'DESPESA',
  'embalagens-frete': 'CUSTO',
}

interface Props {
  ano: number
  /** mes = 0-11, ou null para "Ano inteiro". */
  mes: number | null
  anos: number[]
  onAnoChange: (ano: number) => void
  onMesChange: (mes: number | null) => void
  categorias: CategoriaFinanceira[]
  periodosPorCategoria: FinancePeriodoCategoria[]
  selectedCategoriaId: number | null
  onCategoriaChange: (
    categoriaId: number | null,
    periodo?: FinancePeriodoCategoria,
  ) => void
  selectedTipo: TipoLancamento | ''
  onTipoChange: (tipo: TipoLancamento | '') => void
  onClear: () => void
}

const selectClass =
  'px-3 py-1.5 text-sm border border-gray-200 bg-white focus:outline-none focus:border-black transition-colors font-mono'

const labelClass =
  'block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5'

export function FinanceiroFiltros({
  ano,
  mes,
  anos,
  onAnoChange,
  onMesChange,
  categorias,
  periodosPorCategoria,
  selectedCategoriaId,
  onCategoriaChange,
  selectedTipo,
  onTipoChange,
  onClear,
}: Props) {
  const activeCategorias = categorias.filter((categoria) => categoria.ativo)
  const selectedCategoria = activeCategorias.find(
    (categoria) => categoria.id === selectedCategoriaId,
  )
  const lockedTipo = selectedCategoria
    ? CATEGORY_KIND_BY_SLUG[selectedCategoria.slug]
    : null

  const handleCategoriaChange = (categoriaId: number | null) => {
    const categoria =
      categoriaId === null
        ? null
        : activeCategorias.find((item) => item.id === categoriaId) ?? null
    const periodo = periodosPorCategoria.find(
      (item) => item.categoria_id === (categoria?.id ?? null),
    )
    onCategoriaChange(categoria?.id ?? null, periodo)
    const tipo = categoria ? CATEGORY_KIND_BY_SLUG[categoria.slug] : null
    onTipoChange(tipo ?? '')
  }

  return (
    <div className="flex flex-wrap items-end gap-3">
      <div>
        <label className={labelClass}>Mês</label>
        <select
          value={mes === null ? 'all' : String(mes)}
          onChange={(event) =>
            onMesChange(
              event.target.value === 'all' ? null : Number(event.target.value),
            )
          }
          className={selectClass}
        >
          <option value="all">Ano inteiro</option>
          {MESES_PT.map((nome, index) => (
            <option key={nome} value={index}>
              {nome}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Ano</label>
        <select
          value={String(ano)}
          onChange={(event) => onAnoChange(Number(event.target.value))}
          className={selectClass}
        >
          {anos.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Categoria</label>
        <select
          value={selectedCategoriaId === null ? 'all' : String(selectedCategoriaId)}
          onChange={(event) =>
            handleCategoriaChange(
              event.target.value === 'all' ? null : Number(event.target.value),
            )
          }
          className={selectClass}
        >
          <option value="all">Todas as categorias</option>
          {activeCategorias.map((categoria) => (
            <option key={categoria.id} value={categoria.id}>
              {categoria.nome}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className={labelClass}>Tipo</label>
        <select
          value={selectedTipo === '' ? 'all' : selectedTipo}
          disabled={!!lockedTipo}
          onChange={(event) =>
            onTipoChange(
              event.target.value === 'all'
                ? ''
                : (event.target.value as TipoLancamento),
            )
          }
          className={`${selectClass} disabled:cursor-not-allowed disabled:opacity-50`}
        >
          <option value="all">Todos</option>
          <option value="RECEITA">Entrada</option>
          <option value="DESPESA">Saída</option>
          <option value="CUSTO">Custo</option>
        </select>
      </div>

      <button
        type="button"
        onClick={onClear}
        className="h-9 px-3 text-sm border border-gray-200 text-gray-600 hover:text-black hover:border-gray-400 transition-colors"
      >
        Limpar filtros
      </button>
    </div>
  )
}
