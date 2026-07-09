import { apiClient } from './client'
import type { Subcategoria } from '../types/catalog'

export async function fetchSubcategorias(): Promise<Subcategoria[]> {
  const response = await apiClient.get<Subcategoria[]>('/catalog/subcategorias/')
  return response.data
}

export async function createSubcategoria(
  nome: string,
  categoriaId: number,
): Promise<Subcategoria> {
  const response = await apiClient.post<Subcategoria>(
    '/catalog/subcategorias/',
    { nome, categoria_id: categoriaId },
  )
  return response.data
}
