import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ThemeToggle } from './ThemeToggle'

const NAV = [
  { to: '/', label: 'Início' },
  { to: '/catalogo', label: 'Catálogo' },
  { to: '/finance', label: 'Finance' },
]

export function Topbar() {
  const { pathname } = useLocation()
  const { user, logout } = useAuth()

  return (
    <header className="border-b border-gray-200 bg-white/85 backdrop-blur sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
        <Link
          to="/"
          aria-label="Ir para a página inicial"
          className="flex items-baseline gap-2.5"
        >
          <span className="font-display text-lg font-semibold text-black tracking-tight">
            Controle Interno
          </span>
          {user?.empresa && (
            <span className="hidden sm:inline font-mono text-xs uppercase tracking-wider text-gray-500">
              {user.empresa.nome}
            </span>
          )}
        </Link>

        <div className="flex items-center gap-5">
          <nav className="flex items-stretch gap-1">
            {NAV.map((item) => {
              const active =
                item.to === '/'
                  ? pathname === item.to
                  : pathname === item.to || pathname.startsWith(`${item.to}/`)
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className="relative px-4 h-16 flex items-center text-sm transition-colors"
                >
                  <span className={active ? 'text-black font-medium' : 'text-gray-600 hover:text-black'}>
                    {item.label}
                  </span>
                  {active && (
                    <span className="absolute left-3 right-3 bottom-0 h-[2px] bg-black" />
                  )}
                </Link>
              )
            })}
          </nav>

          <div className="hidden md:flex items-center gap-3 border-l border-gray-200 pl-5">
            <ThemeToggle />

            <div className="text-right">
              <div className="font-mono text-xs text-gray-600">sessão</div>
              <div className="text-sm text-black max-w-40 truncate">
                {user?.empresa?.nome || user?.first_name || user?.username}
              </div>
            </div>
            <button
              type="button"
              onClick={() => logout()}
              className="px-3 py-1.5 text-xs border border-gray-200 text-gray-600 hover:text-black hover:border-gray-400 transition-colors"
            >
              Sair
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
