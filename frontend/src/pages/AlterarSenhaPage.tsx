import { useState, type FormEvent } from 'react'

import { changePassword } from '../api/auth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { mensagemDeErro } from '../utils/apiError'

export function AlterarSenhaPage() {
  useDocumentTitle('Controle Interno — Alterar senha')

  const [senhaAtual, setSenhaAtual] = useState('')
  const [novaSenha, setNovaSenha] = useState('')
  const [confirmarSenha, setConfirmarSenha] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    setSuccess('')
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
      await changePassword({ senha_atual: senhaAtual, nova_senha: novaSenha })
      setSuccess('Senha alterada com sucesso.')
      setSenhaAtual('')
      setNovaSenha('')
      setConfirmarSenha('')
    } catch (err) {
      setError(
        mensagemDeErro(
          err,
          'Não foi possível alterar a senha. Tente novamente.',
        ),
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-8 py-10">
      <div className="max-w-lg">
        <div className="kicker mb-2">Segurança</div>
        <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
          Alterar senha
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          A nova senha passa a valer no próximo login.
        </p>

        <form
          onSubmit={handleSubmit}
          className="mt-6 border border-gray-200 bg-white p-6"
        >
          <div className="space-y-4">
            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Senha atual
              </label>
              <input
                type="password"
                value={senhaAtual}
                onChange={(event) => setSenhaAtual(event.target.value)}
                autoComplete="current-password"
                className="form-input"
                autoFocus
              />
            </div>

            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Nova senha
              </label>
              <input
                type="password"
                value={novaSenha}
                onChange={(event) => setNovaSenha(event.target.value)}
                autoComplete="new-password"
                className="form-input"
              />
            </div>

            <div>
              <label className="block font-mono text-xs uppercase tracking-wider text-gray-600 mb-1.5">
                Confirmar nova senha
              </label>
              <input
                type="password"
                value={confirmarSenha}
                onChange={(event) => setConfirmarSenha(event.target.value)}
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
          {success && (
            <div className="mt-4 border border-gray-300 bg-gray-50 px-3 py-2 text-sm text-gray-900">
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={
              isSubmitting || !senhaAtual || !novaSenha || !confirmarSenha
            }
            className="mt-6 px-6 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'alterando...' : 'Alterar senha'}
          </button>
        </form>
      </div>
    </div>
  )
}
