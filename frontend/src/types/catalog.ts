export type Status = 'ATIVO' | 'INATIVO'

export interface Variacao {
  id: number
  produto_id: number
  produto_nome_site: string
  produto_nome_gestaoclick: string
  produto_descricao_site: string
  produto_descricao_gestaoclick: string
  sku_nuvemshop: string
  id_gestaoclick: string
  codigo_barras: string
  descricao: string
  custo: string
  preco_loja: string
  preco_site: string | null
  margem_percentual: string | null
  preco_promocional: string | null
  margem_promocional_percentual: string | null
  status_nuvemshop: Status
  status_integracao: Status
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface Categoria {
  id: number
  nome: string
  slug: string
  ativo: boolean
}

export interface Subcategoria {
  id: number
  nome: string
  slug: string
  categoria_id: number
  categoria_nome: string
  ativo: boolean
}

export interface Produto {
  id: number
  nome_gestaoclick: string
  nome_site: string
  descricao_produto_gestaoclick: string
  descricao_produto_site: string
  categoria_id: number | null
  categoria_nome: string | null
  subcategoria_id: number | null
  subcategoria_nome: string | null
  ativo: boolean
  criado_em: string
  atualizado_em: string
}

export interface VariacaoComposta {
  id?: number
  sku_nuvemshop: string
  id_gestaoclick: string
  codigo_barras: string
  descricao: string
  custo: string
  preco_loja: string
  preco_site: string | null
  preco_promocional: string | null
  status_nuvemshop: Status
  status_integracao: Status
  ativo: boolean
}

export interface ProdutoComVariacoesPayload {
  nome_gestaoclick: string
  nome_site: string
  descricao_produto_gestaoclick: string
  descricao_produto_site: string
  categoria_id: number | null
  subcategoria_id: number | null
  variacoes: VariacaoComposta[]
}

export interface ProdutoComVariacoesResponse {
  produto: Produto
  variacoes: Variacao[]
}
