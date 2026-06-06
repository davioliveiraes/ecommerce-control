import { apiClient } from './client'
import type { AnalyticsOverview, AnalyticsProdutos } from '../types/analytics'

export async function fetchAnalyticsOverview(): Promise<AnalyticsOverview> {
  const response = await apiClient.get<AnalyticsOverview>(
    '/finance/analytics/overview',
  )
  return response.data
}

export async function fetchAnalyticsProdutos(): Promise<AnalyticsProdutos> {
  const response = await apiClient.get<AnalyticsProdutos>(
    '/finance/analytics/products',
  )
  return response.data
}
