import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { isAxiosError } from 'axios'

import { ThemeToggle } from '../components/ThemeToggle'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { formatCnpj, somenteDigitosCnpj } from '../utils/cnpj'

type Mode = 'login' | 'register'

function mensagemDeErro(err: unknown, fallback: string): string {
  if (isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: unknown } | undefined)
      ?.detail
    if (typeof detail === 'string') return detail
    // Erros de validação do Ninja (422): lista de {msg, ...}
    if (Array.isArray(detail) && detail.length > 0) {
      const primeiro = detail[0] as { msg?: string }
      if (typeof primeiro.msg === 'string')
        return primeiro.msg.replace(/^Value error,\s*/, '')
    }
  }
  return fallback
}

export function LoginPage() {
  useDocumentTitle('Controle Interno — Login')

  const { isAuthenticated, isLoading, login, register } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [usuario, setUsuario] = useState('')
  const [nomeEmpresa, setNomeEmpresa] = useState('')
  const [cnpj, setCnpj] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const from =
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname || '/'

  if (!isLoading && isAuthenticated) {
    return <Navigate to={from} replace />
  }

  const trocarModo = (novo: Mode) => {
    setMode(novo)
    setError('')
  }

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
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

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    if (somenteDigitosCnpj(cnpj).length !== 14) {
      setError('Informe um CNPJ completo (14 dígitos).')
      return
    }
    const usuarioNormalizado = usuario.trim().toLowerCase()
    if (!/^[a-z0-9][a-z0-9._-]{2,29}$/.test(usuarioNormalizado)) {
      setError(
        'O usuário deve ter de 3 a 30 caracteres, começar com letra ou número e usar apenas letras minúsculas, números, ponto, hífen e underline.',
      )
      return
    }
    if (password.length < 8) {
      setError('A senha deve ter pelo menos 8 caracteres.')
      return
    }
    if (password !== confirmPassword) {
      setError('As senhas não conferem.')
      return
    }
    setIsSubmitting(true)
    try {
      await register({
        nome: nomeEmpresa.trim(),
        cnpj: somenteDigitosCnpj(cnpj),
        username: usuarioNormalizado,
        email: email.trim(),
        password,
      })
      navigate('/', { replace: true })
    } catch (err) {
      setError(
        mensagemDeErro(err, 'Não foi possível concluir o cadastro. Tente novamente.'),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const isRegister = mode === 'register'

  return (
    <main className="relative min-h-screen bg-white flex">
      <ThemeToggle className="absolute top-6 right-6 z-10" />

      <section className="hidden lg:flex w-[42%] border-r border-gray-200 bg-gray-50 px-12 py-10 flex-col justify-between">
        <div className="font-display text-xl font-semibold text-black tracking-tight">
          Controle Interno
        </div>
        <div>
          <div className="kicker mb-4">Para lojistas com CNPJ</div>
          <h1 className="font-display text-4xl font-semibold text-black tracking-tight leading-tight max-w-md">
            O catálogo e o financeiro da sua loja em um só lugar.
          </h1>
          <p className="text-sm text-gray-600 leading-relaxed mt-4 max-w-sm">
            Cadastre sua empresa e gerencie produtos, preços, lançamentos e
            relatórios da sua operação de ecommerce.
          </p>
        </div>
        <div className="font-mono text-xs text-gray-600">
          API protegida por token bearer
        </div>
      </section>

      <section className="flex-1 flex items-center justify-center px-6 py-10">
        <div className="w-full max-w-sm">
          <div className="mb-4 grid grid-cols-2 border border-gray-200">
            <button
              type="button"
              onClick={() => trocarModo('login')}
              className={`px-4 py-2 text-sm transition-colors ${
                !isRegister
                  ? 'bg-black text-white'
                  : 'bg-white text-gray-600 hover:text-black'
              }`}
            >
              Entrar
            </button>
            <button
              type="button"
              onClick={() => trocarModo('register')}
              className={`px-4 py-2 text-sm transition-colors ${
                isRegister
                  ? 'bg-black text-white'
                  : 'bg-white text-gray-600 hover:text-black'
              }`}
            >
              Criar conta
            </button>
          </div>

          {!isRegister ? (
            <form
              onSubmit={handleLogin}
              className="border border-gray-200 bg-white p-6"
            >
              <div className="mb-6">
                <div className="kicker mb-2">Autenticação</div>
                <h2 className="font-display text-2xl font-semibold text-black tracking-tight">
                  Entrar no sistema
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Use o usuário ou e-mail e a senha cadastrados pela sua
                  empresa.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    E-mail ou usuário
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
                <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting || !username || !password}
                className="mt-6 w-full px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'entrando...' : 'Entrar'}
              </button>
            </form>
          ) : (
            <form
              onSubmit={handleRegister}
              className="border border-gray-200 bg-white p-6"
            >
              <div className="mb-6">
                <div className="kicker mb-2">Cadastro</div>
                <h2 className="font-display text-2xl font-semibold text-black tracking-tight">
                  Criar conta da empresa
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Destinado a empresas com CNPJ. Sua loja terá catálogo e
                  financeiro próprios.
                </p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    Nome da empresa
                  </label>
                  <input
                    type="text"
                    value={nomeEmpresa}
                    onChange={(event) => setNomeEmpresa(event.target.value)}
                    autoComplete="organization"
                    className="form-input"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    CNPJ
                  </label>
                  <input
                    type="text"
                    value={cnpj}
                    onChange={(event) => setCnpj(formatCnpj(event.target.value))}
                    inputMode="numeric"
                    placeholder="00.000.000/0000-00"
                    className="form-input"
                  />
                </div>

                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    Usuário
                  </label>
                  <input
                    type="text"
                    value={usuario}
                    onChange={(event) => setUsuario(event.target.value)}
                    autoComplete="username"
                    placeholder="ex.: minhaloja"
                    className="form-input"
                  />
                  <p className="mt-1 text-xs text-gray-600">
                    Usado no login, junto com o e-mail.
                  </p>
                </div>

                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    E-mail
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    autoComplete="email"
                    className="form-input"
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
                    autoComplete="new-password"
                    className="form-input"
                  />
                </div>

                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    Confirmar senha
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(event) => setConfirmPassword(event.target.value)}
                    autoComplete="new-password"
                    className="form-input"
                  />
                </div>
              </div>

              {error && (
                <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={
                  isSubmitting ||
                  !nomeEmpresa ||
                  !cnpj ||
                  !usuario ||
                  !email ||
                  !password ||
                  !confirmPassword
                }
                className="mt-6 w-full px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'criando conta...' : 'Criar conta'}
              </button>
            </form>
          )}
        </div>
      </section>
    </main>
  )
}
