import { apiClient } from './client'
import type {
  LancamentoFinanceiro,
  LancamentoFinanceiroFilters,
  LancamentoFinanceiroPayload,
} from '../types/finance'

function cleanFilters(params?: LancamentoFinanceiroFilters) {
  if (!params) return undefined

  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => {
      return value !== '' && value !== null && value !== undefined
    }),
  )
}

export async function fetchLancamentosFinanceiros(
  params?: LancamentoFinanceiroFilters,
): Promise<LancamentoFinanceiro[]> {
  const response = await apiClient.get<LancamentoFinanceiro[]>(
    '/finance/lancamentos/',
    {
      params: cleanFilters(params),
    },
  )
  return response.data
}

export async function fetchLancamentoFinanceiro(
  id: number,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.get<LancamentoFinanceiro>(
    `/finance/lancamentos/${id}`,
  )
  return response.data
}

export async function createLancamentoFinanceiro(
  payload: LancamentoFinanceiroPayload,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.post<LancamentoFinanceiro>(
    '/finance/lancamentos/',
    payload,
  )
  return response.data
}

export async function updateLancamentoFinanceiro(
  id: number,
  payload: LancamentoFinanceiroPayload,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.put<LancamentoFinanceiro>(
    `/finance/lancamentos/${id}`,
    payload,
  )
  return response.data
}

export async function archiveLancamentoFinanceiro(
  id: number,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.post<LancamentoFinanceiro>(
    `/finance/lancamentos/${id}/archive`,
  )
  return response.data
}

export async function marcarLancamentoPago(
  id: number,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.post<LancamentoFinanceiro>(
    `/finance/lancamentos/${id}/marcar-pago`,
  )
  return response.data
}

export async function restoreLancamentoFinanceiro(
  id: number,
): Promise<LancamentoFinanceiro> {
  const response = await apiClient.patch<LancamentoFinanceiro>(
    `/finance/lancamentos/${id}`,
    { ativo: true },
  )
  return response.data
}
