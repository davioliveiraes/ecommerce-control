import { Link } from 'react-router-dom'

import { CatalogoGrid } from '../components/catalogo/CatalogoGrid'
import { useAuth } from '../hooks/useAuth'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function CatalogoPage() {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''

  useDocumentTitle(nomeEmpresa ? `Catálogo — ${nomeEmpresa}` : 'Catálogo')

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <div className="flex items-start justify-between gap-6 mb-5">
        <div className="min-w-0">
          <div className="kicker mb-1.5">Módulo 01</div>
          <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
            Catálogo{nomeEmpresa ? ` — ${nomeEmpresa}` : ''}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Gestão dos produtos, variações, preços e integração com NuvemShop.
          </p>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 bg-white text-gray-700 hover:border-black hover:text-black transition-colors"
          >
            <IconHome />
            Inicio
          </Link>

          <Link
            to="/catalogo/produto/novo"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors"
          >
            <IconPlus />
            Adicionar Produto
          </Link>
        </div>
      </div>

      <CatalogoGrid />
    </div>
  )
}

function IconHome() {
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
      <path d="m3 10.5 9-7 9 7" />
      <path d="M5 10v10h14V10" />
      <path d="M9 20v-6h6v6" />
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
