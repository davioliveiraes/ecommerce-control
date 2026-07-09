import { apiClient } from './client'
import type { Categoria } from '../types/catalog'

export async function fetchCategorias(): Promise<Categoria[]> {
  const response = await apiClient.get<Categoria[]>('/catalog/categorias/')
  return response.data
}

export async function createCategoria(nome: string): Promise<Categoria> {
  const response = await apiClient.post<Categoria>('/catalog/categorias/', {
    nome,
  })
  return response.data
}
