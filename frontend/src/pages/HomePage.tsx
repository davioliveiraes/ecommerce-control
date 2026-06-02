import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchHealth } from '../api/health'
import { useDocumentTitle } from '../hooks/useDocumentTitle'

const MODULES = [
  {
    index: '01',
    to: '/catalogo',
    title: 'Ibeize Catálogo',
    description:
      'Base de produtos do Site Ibeize em tabela editável. Cadastro, variações, preços, margens e integração GestãoClick ↔ Nuvemshop.',
    Icon: IconGrid,
  },
  {
    index: '02',
    to: '/finance',
    title: 'Ibeize Finance',
    description:
      'Painel consolidado de custos, receitas e despesas com séries temporais e indicadores de desempenho.',
    Icon: IconChart,
  },
]

export function HomePage() {
  useDocumentTitle('Controle Interno — Site Ibeize')

  const { data, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: fetchHealth,
    refetchOnWindowFocus: false,
  })

  return (
    <div className="h-[calc(100vh-4rem)] overflow-hidden">
      <div className="h-full max-w-6xl mx-auto px-8 py-10 flex flex-col">
        <div className="text-center pt-2 pb-8 shrink-0">
          <div className="text-xs uppercase tracking-widest text-slate-500 mb-4">
            Controle interno · Site Ibeize
          </div>

          <h1 className="font-display whitespace-nowrap font-semibold text-black leading-[1.02] text-[clamp(1.5rem,5vw,4rem)]">
            Controle Interno — Site Ibeize
          </h1>

          <p className="mt-4 text-lg text-gray-600">
            Painel interno de gestão para o Site Ibeize
          </p>
          <div className="mx-auto mt-6 h-[2px] w-16 bg-orange" />
        </div>

        <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-2 gap-px bg-gray-200 border border-gray-200">
          {MODULES.map(({ index, to, title, description, Icon }) => (
            <Link
              key={to}
              to={to}
              className="group relative bg-white p-8 flex flex-col hover:bg-orange-soft transition-colors"
            >
              <div className="flex items-start justify-between mb-6">
                <span className="kicker">{index} / 02</span>
                <Icon />
              </div>

              <h2 className="font-display text-2xl font-semibold text-black mb-2 tracking-tight">
                {title}
              </h2>
              <p className="text-gray-600 leading-relaxed text-sm flex-1">
                {description}
              </p>

              <span className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-orange-dark group-hover:gap-3 transition-all">
                Acessar módulo
                <ArrowRight />
              </span>
            </Link>
          ))}
        </div>

        <div className="shrink-0 flex items-center justify-between border-t border-gray-200 pt-4 mt-4">
          <span className="kicker">Status do sistema</span>
          <ApiStatus isLoading={isLoading} isError={isError} data={data} />
        </div>
      </div>
    </div>
  )
}

function ApiStatus({
  isLoading,
  isError,
  data,
}: {
  isLoading: boolean
  isError: boolean
  data?: { status: string }
}) {
  const dotColor = isLoading
    ? 'bg-gray-400'
    : isError
      ? 'bg-orange'
      : 'bg-navy'
  const label = isLoading
    ? 'verificando'
    : isError
      ? 'offline'
      : `online · ${data?.status ?? 'ok'}`

  return (
    <span className="inline-flex items-center gap-2.5 font-mono text-xs text-gray-600">
      <span className="relative flex h-1.5 w-1.5">
        {!isError && !isLoading && (
          <span className="absolute inset-0 rounded-full bg-navy/40 animate-ping" />
        )}
        <span className={`relative inline-flex h-1.5 w-1.5 rounded-full ${dotColor}`} />
      </span>
      api · {label}
    </span>
  )
}

function IconGrid() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-orange">
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
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
