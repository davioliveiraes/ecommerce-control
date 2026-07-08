export interface ColunaRelatorio {
  chave: string
  label: string
  selecionadaPorPadrao: boolean
}

export const COLUNAS_CATALOGO: ColunaRelatorio[] = [
  { chave: 'sku', label: 'SKU', selecionadaPorPadrao: true },
  {
    chave: 'produto_descricao_site',
    label: 'Produto (Site)',
    selecionadaPorPadrao: true,
  },
  {
    chave: 'produto_descricao_gestaoclick',
    label: 'Produto (GestãoClick)',
    selecionadaPorPadrao: false,
  },
  { chave: 'variacao', label: 'Variação', selecionadaPorPadrao: true },
  { chave: 'categoria', label: 'Categoria', selecionadaPorPadrao: false },
  { chave: 'subcategoria', label: 'Subcategoria', selecionadaPorPadrao: false },
  { chave: 'custo', label: 'Custo', selecionadaPorPadrao: false },
  { chave: 'preco_loja', label: 'Preço Loja', selecionadaPorPadrao: false },
  { chave: 'preco_site', label: 'Preço Site', selecionadaPorPadrao: true },
  {
    chave: 'preco_promocional',
    label: 'Preço Promocional',
    selecionadaPorPadrao: false,
  },
  { chave: 'margem_percentual', label: 'Margem %', selecionadaPorPadrao: false },
  {
    chave: 'margem_promocional_percentual',
    label: 'Margem Promoção',
    selecionadaPorPadrao: false,
  },
  {
    chave: 'status_nuvemshop',
    label: 'Status NuvemShop',
    selecionadaPorPadrao: false,
  },
  {
    chave: 'status_integracao',
    label: 'Status Integração',
    selecionadaPorPadrao: false,
  },
]

export const COLUNAS_FINANCE: ColunaRelatorio[] = [
  { chave: 'data', label: 'Data', selecionadaPorPadrao: true },
  { chave: 'descricao', label: 'Descrição', selecionadaPorPadrao: true },
  { chave: 'tipo', label: 'Tipo', selecionadaPorPadrao: true },
  { chave: 'categoria', label: 'Categoria', selecionadaPorPadrao: true },
  { chave: 'valor', label: 'Valor', selecionadaPorPadrao: true },
  { chave: 'status', label: 'Status', selecionadaPorPadrao: true },
  { chave: 'observacoes', label: 'Observações', selecionadaPorPadrao: false },
]
