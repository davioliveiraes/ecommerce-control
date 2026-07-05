import { useState, type FormEvent } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { resetPassword } from '../api/auth'
import { PasswordInput } from '../components/PasswordInput'
import { ThemeToggle } from '../components/ThemeToggle'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { mensagemDeErro } from '../utils/apiError'

export function RedefinirSenhaPage() {
  useDocumentTitle('Controle Interno — Redefinir senha')

  const [searchParams] = useSearchParams()
  const uid = searchParams.get('uid') ?? ''
  const token = searchParams.get('token') ?? ''

  const [novaSenha, setNovaSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [error, setError] = useState('')
  const [sucesso, setSucesso] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const linkInvalido = !uid || !token

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    if (novaSenha.length < 8) {
      setError('A nova senha deve ter pelo menos 8 caracteres.')
      return
    }
    if (novaSenha !== confirmarSenha) {
      setError('As senhas não conferem.')
      return
    }
    setIsSubmitting(true)
    try {
      await resetPassword({ uid, token, nova_senha: novaSenha })
      setSucesso(true)
    } catch (err) {
      setError(
        mensagemDeErro(
          err,
          'Não foi possível redefinir a senha. Solicite um novo link.',
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="relative min-h-screen bg-white flex items-center justify-center px-6 py-10">
      <ThemeToggle className="absolute top-6 right-6 z-10" />

      <div className="w-full max-w-sm">
        <div className="border border-gray-200 bg-white p-6">
          <div className="mb-6">
            <div className="kicker mb-2">Recuperação</div>
            <h1 className="font-display text-2xl font-semibold text-black tracking-tight">
              Redefinir senha
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Crie a nova senha de acesso da sua conta.
            </p>
          </div>

          {linkInvalido ? (
            <div className="border border-gray-300 bg-gray-50 px-3 py-3 text-sm text-gray-900">
              Link de redefinição inválido ou incompleto.{' '}
              <Link
                to="/esqueci-senha"
                className="underline underline-offset-4 decoration-gray-400 hover:text-black"
              >
                Solicite um novo link
              </Link>
              .
            </div>
          ) : sucesso ? (
            <div>
              <div className="border border-gray-300 bg-gray-50 px-3 py-3 text-sm text-gray-900">
                Senha redefinida com sucesso. Você já pode entrar com a nova
                senha.
              </div>
              <Link
                to="/login"
                className="mt-6 block w-full px-4 py-2 text-center text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors"
              >
                Ir para o login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    Nova senha
                  </label>
                  <PasswordInput
                    value={novaSenha}
                    onChange={(event) => setNovaSenha(event.target.value)}
                    autoComplete="new-password"
                    autoFocus
                  />
                </div>

                <div>
                  <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                    Confirmar nova senha
                  </label>
                  <PasswordInput
                    value={confirmarSenha}
                    onChange={(event) => setConfirmarSenha(event.target.value)}
                    autoComplete="new-password"
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
                disabled={isSubmitting || !novaSenha || !confirmarSenha}
                className="mt-6 w-full px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'redefinindo...' : 'Redefinir senha'}
              </button>
            </form>
          )}

          {!sucesso && !linkInvalido && (
            <div className="mt-4 text-center">
              <Link
                to="/login"
                className="text-xs text-gray-600 hover:text-black underline underline-offset-4 decoration-gray-400 transition-colors"
              >
                Voltar para o login
              </Link>
            </div>
          )}
        </div>
      </div>
    </main>
  )
}
