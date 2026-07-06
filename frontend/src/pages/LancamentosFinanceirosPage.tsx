import { useNavigate } from 'react-router-dom'

import { LancamentosFinanceirosGrid } from '../components/finance/LancamentosFinanceirosGrid'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function LancamentosFinanceirosPage() {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''

  useDocumentTitle(`Lançamentos Financeiros — ${nomeEmpresa}`)

  const navigate = useNavigate()

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <div className="flex items-start justify-between gap-6 mb-5">
        <div className="min-w-0">
          <button
            type="button"
            onClick={() => navigate('/finance')}
            className="inline-flex items-center gap-1.5 text-xs text-gray-600 hover:text-black transition-colors mb-3 font-mono"
          >
            <IconArrowLeft />
            voltar ao dashboard financeiro
          </button>
          <div className="kicker mb-1.5">Módulo 02</div>
          <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
            Lançamentos Financeiros — {nomeEmpresa}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Entradas e saídas operacionais com status, categoria e ações de
            baixa ou arquivamento.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate('/finance/lancamentos/novo')}
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors shrink-0"
        >
          <IconPlus />
          Novo lançamento
        </button>
      </div>

      <LancamentosFinanceirosGrid />
    </div>
  )
}

function IconArrowLeft() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M19 12H5" />
      <path d="m12 19-7-7 7-7" />
    </svg>
  )
}

function IconPlus() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  )
}
