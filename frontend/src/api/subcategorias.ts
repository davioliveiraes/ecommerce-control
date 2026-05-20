import { apiClient } from './client'
import type { Subcategoria } from '../types/catalog'

export async function fetchSubcategorias(): Promise<Subcategoria[]> {
  const response = await apiClient.get<Subcategoria[]>('/catalog/subcategorias/')
  return response.data
}
