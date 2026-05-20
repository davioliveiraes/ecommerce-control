import { apiClient } from './client'
import type { Marca } from '../types/catalog'

export async function fetchMarcas(): Promise<Marca[]> {
  const response = await apiClient.get<Marca[]>('/catalog/marcas/')
  return response.data
}
