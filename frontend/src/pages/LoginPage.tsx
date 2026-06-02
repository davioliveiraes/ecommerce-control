import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function LoginPage() {
  useDocumentTitle('Login — Controle Interno Site Ibeize')

  const { isAuthenticated, isLoading, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const from =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname || '/'

  if (!isLoading && isAuthenticated) {
    return <Navigate to={from} replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await login({ username, password })
      navigate(from, { replace: true })
    } catch {
      setError('Usuário ou senha inválidos.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="min-h-screen bg-white flex">
      <section className="hidden lg:flex w-[42%] border-r border-gray-200 bg-gray-50 px-12 py-10 flex-col justify-between">
        <img src="/brand/logo_ibeize.png" alt="Ibeize" className="h-10 w-fit" />
        <div>
          <div className="kicker mb-4">v1.0.0</div>
          <h1 className="font-display text-4xl font-semibold text-black tracking-tight leading-tight max-w-md">
            Controle interno de catálogo e financeiro.
          </h1>
          <p className="text-sm text-gray-600 leading-relaxed mt-4 max-w-sm">
            Acesso restrito para operação da Ibeize. Entre com seu usuário do
            Django para continuar.
          </p>
        </div>
        <div className="font-mono text-xs text-gray-600">
          API protegida por token bearer
        </div>
      </section>

      <section className="flex-1 flex items-center justify-center px-6 py-10">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-sm border border-gray-200 bg-white p-6"
        >
          <div className="mb-6">
            <div className="kicker mb-2">Autenticação</div>
            <h2 className="font-display text-2xl font-semibold text-black tracking-tight">
              Entrar no sistema
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              Use as credenciais cadastradas no Django Admin.
            </p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Usuário
              </label>
              <input
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                autoComplete="username"
                className="form-input"
                autoFocus
              />
            </div>

            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Senha
              </label>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                className="form-input"
              />
            </div>
          </div>

          {error && (
            <div className="mt-4 border border-orange/40 bg-orange-soft px-3 py-2 text-sm text-orange-dark">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !username || !password}
            className="mt-6 w-full px-4 py-2 text-sm border border-orange bg-orange text-white hover:bg-orange-dark hover:border-orange-dark transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'entrando...' : 'Entrar'}
          </button>
        </form>
      </section>
    </main>
  )
}
