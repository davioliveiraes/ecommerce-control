export type TipoLancamento = 'CUSTO' | 'RECEITA' | 'DESPESA'
export type StatusLancamento = 'PENDENTE' | 'PAGO'

export interface CategoriaFinanceira {
  id: number
  nome: string
  slug: string
  cor_hex: string
  ativo: boolean
}

export interface LancamentoFinanceiro {
  id: number
  descricao: string
  tipo: TipoLancamento
  categoria_id: number | null
  categoria_nome: string | null
  categoria_cor_hex: string | null
  valor: string
  data_lancamento: string
  status: StatusLancamento
  observacoes: string
  ativo: boolean
}

export interface LancamentoFinanceiroPayload {
  descricao: string
  tipo: TipoLancamento
  categoria_id: number | null
  valor: string
  data_lancamento: string
  status: StatusLancamento
  observacoes: string
}

export interface LancamentoFinanceiroFilters {
  q?: string
  inativos?: boolean
  tipo?: TipoLancamento | ''
  status?: StatusLancamento | ''
  categoria_id?: number | null
  data_inicio?: string
  data_fim?: string
}
