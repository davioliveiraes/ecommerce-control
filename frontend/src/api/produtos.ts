import { apiClient } from './client'
import type {
  Produto,
  ProdutoComVariacoesPayload,
  ProdutoComVariacoesResponse,
} from '../types/catalog'

export async function fetchProduto(id: number): Promise<Produto> {
  const response = await apiClient.get<Produto>(`/catalog/produtos/${id}`)
  return response.data
}

export async function saveProdutoComVariacoes(
  id: number,
  payload: ProdutoComVariacoesPayload,
): Promise<ProdutoComVariacoesResponse> {
  const response = await apiClient.put<ProdutoComVariacoesResponse>(
    `/catalog/produtos/${id}/com-variacoes`,
    payload,
  )
  return response.data
}
