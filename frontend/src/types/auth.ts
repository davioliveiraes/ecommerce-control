export interface EmpresaInfo {
  id: number
  nome: string
  cnpj: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_staff: boolean
  empresa: EmpresaInfo | null
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  nome: string
  cnpj: string
  username: string
  email: string
  password: string
}

export interface LoginResponse {
  token: string
  token_type: 'Bearer'
  user: AuthUser
}
