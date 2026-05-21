import { Link } from 'react-router-dom'

export function FinancePage() {
  return (
    <div className="max-w-7xl mx-auto px-8 py-10">
      <div className="mb-8">
        <div className="kicker mb-2">Módulo 02</div>
        <h1 className="font-display text-4xl font-semibold text-black tracking-tight mb-2">
          Finance
        </h1>
        <p className="text-gray-600 max-w-2xl">
          Operação financeira com visão de dashboard e controle dos lançamentos
          de entrada e saída.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-gray-200 border border-gray-200">
        <Link
          to="/finance/lancamentos"
          className="group bg-white p-7 hover:bg-orange-soft transition-colors"
        >
          <div className="flex items-start justify-between mb-5">
            <span className="kicker">Lançamentos</span>
            <IconList />
          </div>
          <h2 className="font-display text-2xl font-semibold text-black mb-2 tracking-tight">
            Lançamentos Financeiros
          </h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            Liste, filtre, cadastre, edite, marque como pago ou arquive
            receitas, custos e despesas.
          </p>
          <span className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-orange-dark group-hover:gap-3 transition-all">
            Acessar lançamentos
            <ArrowRight />
          </span>
        </Link>

        <div className="bg-white p-7">
          <div className="flex items-start justify-between mb-5">
            <span className="kicker">Dashboard</span>
            <IconChart />
          </div>
          <h2 className="font-display text-2xl font-semibold text-black mb-2 tracking-tight">
            Indicadores
          </h2>
          <p className="text-sm text-gray-600 leading-relaxed">
            Resumo financeiro consolidado por período, tipo e status para apoio
            à gestão operacional.
          </p>
        </div>
      </div>
    </div>
  )
}

function IconList() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-orange">
      <path d="M8 6h13" />
      <path d="M8 12h13" />
      <path d="M8 18h13" />
      <path d="M3 6h.01" />
      <path d="M3 12h.01" />
      <path d="M3 18h.01" />
    </svg>
  )
}

function IconChart() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-orange">
      <path d="M3 21h18" />
      <path d="M6 18V10" />
      <path d="M11 18V6" />
      <path d="M16 18v-5" />
      <path d="M21 18v-9" />
    </svg>
  )
}

function ArrowRight() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75">
      <path d="M5 12h14" />
      <path d="m13 6 6 6-6 6" />
    </svg>
  )
}
