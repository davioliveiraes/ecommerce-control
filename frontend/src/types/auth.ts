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

export interface UpdateEmpresaPayload {
  nome: string
  cnpj: string
  username: string
  email: string
}

export interface ChangePasswordPayload {
  senha_atual: string
  nova_senha: string
}

export interface ForgotPasswordPayload {
  email: string
}

export interface ResetPasswordPayload {
  uid: string
  token: string
  nova_senha: string
}

export interface LoginResponse {
  token: string
  token_type: 'Bearer'
  user: AuthUser
}
