import { apiClient } from './client'
import type { CategoriaFinanceira } from '../types/finance'

export async function fetchCategoriasFinanceiras(): Promise<
  CategoriaFinanceira[]
> {
  const response =
    await apiClient.get<CategoriaFinanceira[]>('/finance/categorias/')
  return response.data
}
