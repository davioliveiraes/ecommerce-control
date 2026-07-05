import { useEffect, useState, type FormEvent } from 'react'

import { updateEmpresa } from '../api/auth'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { mensagemDeErro } from '../utils/apiError'
import { formatCnpj, somenteDigitosCnpj } from '../utils/cnpj'

export function EmpresaPage() {
  useDocumentTitle('Controle Interno — Dados da empresa')

  const { user, refreshUser } = useAuth()

  const [nome, setNome] = useState('')
  const [cnpj, setCnpj] = useState('')
  const [usuario, setUsuario] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (!user) return
    setNome(user.empresa?.nome ?? user.first_name)
    setCnpj(formatCnpj(user.empresa?.cnpj ?? ''))
    setUsuario(user.username)
    setEmail(user.email)
  }, [user])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    if (nome.trim().length < 2) {
      setError('Informe o nome da empresa.')
      return
    }
    if (somenteDigitosCnpj(cnpj).length !== 14) {
      setError('Informe um CNPJ completo (14 dígitos).')
      return
    }
    setIsSubmitting(true)
    try {
      await updateEmpresa({
        nome: nome.trim(),
        cnpj: somenteDigitosCnpj(cnpj),
        username: usuario.trim().toLowerCase(),
        email: email.trim().toLowerCase(),
      })
      await refreshUser()
      setSuccess('Dados da empresa atualizados.')
    } catch (err) {
      setError(
        mensagemDeErro(err, 'Não foi possível salvar. Tente novamente.'),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-8 py-10">
      <div className="max-w-lg">
        <div className="kicker mb-2">Perfil</div>
        <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
          Dados da empresa
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          Informações da empresa e credenciais de acesso ao sistema.
        </p>

        <form
          onSubmit={handleSubmit}
          className="mt-6 border border-gray-200 bg-white p-6"
        >
          <div className="space-y-4">
            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Nome da empresa
              </label>
              <input
                type="text"
                value={nome}
                onChange={(event) => setNome(event.target.value)}
                autoComplete="organization"
                className="form-input"
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
          </div>

          {error && (
            <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
              {error}
            </div>
          )}
          {success && (
            <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting || !nome || !cnpj || !usuario || !email}
            className="mt-6 px-6 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'salvando...' : 'Salvar alterações'}
          </button>
        </form>
      </div>
    </div>
  )
}
