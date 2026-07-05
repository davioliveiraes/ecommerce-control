import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

import { forgotPassword } from '../api/auth'
import { ThemeToggle } from '../components/ThemeToggle'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { mensagemDeErro } from '../utils/apiError'

export function EsqueciSenhaPage() {
  useDocumentTitle('Controle Interno — Recuperar senha')

  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [enviado, setEnviado] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await forgotPassword({ email: email.trim().toLowerCase() })
      setEnviado(true)
    } catch (err) {
      setError(
        mensagemDeErro(err, 'Não foi possível enviar o link. Tente novamente.'),
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
              Esqueceu a senha?
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Informe o e-mail da sua conta e enviaremos um link para criar
              uma nova senha.
            </p>
          </div>

          {enviado ? (
            <div className="border border-gray-300 bg-gray-50 px-3 py-3 text-sm text-gray-900">
              Se o e-mail estiver cadastrado, você receberá o link de
              redefinição em instantes. Confira também a caixa de spam.
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
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
                  autoFocus
                />
              </div>

              {error && (
                <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={isSubmitting || !email}
                className="mt-6 w-full px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'enviando...' : 'Enviar link de redefinição'}
              </button>
            </form>
          )}

          <div className="mt-4 text-center">
            <Link
              to="/login"
              className="text-xs text-gray-600 hover:text-black underline underline-offset-4 decoration-gray-400 transition-colors"
            >
              Voltar para o login
            </Link>
          </div>
        </div>
      </div>
    </main>
  )
}
