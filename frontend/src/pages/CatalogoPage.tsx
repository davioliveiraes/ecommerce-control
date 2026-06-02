import { Link } from 'react-router-dom'

import { CatalogoGrid } from '../components/catalogo/CatalogoGrid'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

export function CatalogoPage() {
  useDocumentTitle('Catálogo — Site Ibeize')

  return (
    <div className="max-w-[1600px] mx-auto px-8 py-6">
      <div className="flex items-start justify-between gap-6 mb-5">
        <div className="min-w-0">
          <div className="kicker mb-1.5">Módulo 01</div>
          <h1 className="font-display text-3xl font-semibold text-black tracking-tight">
            Catálogo — Site Ibeize
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            Gestão dos produtos, variações, preços e integração do Site Ibeize.
          </p>
        </div>

        <Link
          to="/"
          className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 bg-white text-gray-700 hover:border-orange hover:text-orange transition-colors shrink-0"
        >
          <IconHome />
          Inicio
        </Link>
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
