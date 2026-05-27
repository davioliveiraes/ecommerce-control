export type TipoLancamento = 'CUSTO' | 'RECEITA' | 'DESPESA'
export type StatusLancamento = 'PENDENTE' | 'PAGO'
export type FormaPagamento =
  | ''
  | 'PIX'
  | 'CARTAO_CREDITO'
  | 'BOLETO'
  | 'NUVEMPAGO'
  | 'OUTRO'
export type MeioPagamento =
  | ''
  | 'NUVEMPAGO'
  | 'MERCADO_PAGO'
  | 'PAGSEGURO'
  | 'MANUAL'
  | 'OUTRO'

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
  forma_pagamento: FormaPagamento
  meio_pagamento: MeioPagamento
  quantidade_parcelas: number | null
  quantidade_vendas: number
  fonte_trafego: string
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
  forma_pagamento: FormaPagamento
  meio_pagamento: MeioPagamento
  quantidade_parcelas: number | null
  quantidade_vendas: number
  fonte_trafego: string
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

export interface FinanceKpis {
  custo_total: string
  receita_total: string
  despesa_total: string
  lucro: string
}

export interface FinancePontoMensal {
  mes: string
  custo: string
  receita: string
  despesa: string
}

export interface FinanceFatiaCategoria {
  categoria_id: number | null
  categoria_nome: string
  categoria_cor_hex: string
  valor: string
}

export interface FinanceMetricaReceitaVendas {
  chave: string
  nome: string
  receita: string
  vendas: number
}

export interface FinanceDashboard {
  kpis: FinanceKpis
  serie_mensal: FinancePontoMensal[]
  receitas_por_categoria: FinanceFatiaCategoria[]
  despesas_por_categoria: FinanceFatiaCategoria[]
  custos_por_categoria: FinanceFatiaCategoria[]
  receita_vendas_por_forma_pagamento: FinanceMetricaReceitaVendas[]
  receita_vendas_por_meio_pagamento: FinanceMetricaReceitaVendas[]
  receita_vendas_por_parcelas: FinanceMetricaReceitaVendas[]
}

export interface FinanceDashboardFilters {
  data_inicio?: string
  data_fim?: string
  categoria_id?: number | null
  incluir_pendentes?: boolean
}
