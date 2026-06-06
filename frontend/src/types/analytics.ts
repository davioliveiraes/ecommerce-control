export type KpiFormato = 'inteiro' | 'moeda'

export interface KpiSerie {
  valor: number | string
  formato: KpiFormato
  serie: Array<number | string>
  labels: string[]
}

export interface KpiOverviewSet {
  visitas: KpiSerie
  vendas: KpiSerie
  receita: KpiSerie
  ticket_medio: KpiSerie
}

export interface BehaviorItem {
  label: string
  valor: number
}

export interface ConversionItem {
  label: string
  valor_percentual: number
  detalhe?: string | null
}

export interface AnalyticsOverview {
  ultima_atualizacao: string
  kpis: KpiOverviewSet
  comportamento_visitantes: BehaviorItem[]
  comportamento_checkout: BehaviorItem[]
  conversoes: ConversionItem[]
}

export interface ProdutoRanking {
  sku: string
  nome: string
  marca: string
  valor_principal: string
  valor_secundario?: string | null
}

export interface AnalyticsProdutos {
  mais_vendidos: ProdutoRanking[]
  mais_visualizados: ProdutoRanking[]
  estoque_critico: ProdutoRanking[]
  margem_ranking: ProdutoRanking[]
}
