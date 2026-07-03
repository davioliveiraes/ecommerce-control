import { apiClient } from './client'
import type {
  AuthUser,
  LoginPayload,
  LoginResponse,
  RegisterPayload,
} from '../types/auth'

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', payload)
  return response.data
}

export async function register(
  payload: RegisterPayload,
): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>(
    '/auth/register',
    payload,
  )
  return response.data
}

export async function fetchMe(): Promise<AuthUser> {
  const response = await apiClient.get<AuthUser>('/auth/me')
  return response.data
}

export async function logout(): Promise<{ ok: boolean }> {
  const response = await apiClient.post<{ ok: boolean }>('/auth/logout')
  return response.data
}
