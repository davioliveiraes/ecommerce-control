import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ThemeToggle } from './ThemeToggle'

const NAV = [
  { to: '/', label: 'Início' },
  { to: '/catalogo', label: 'Catálogo' },
  { to: '/finance', label: 'Financeiro' },
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
            <span
              title={user.empresa.nome}
              className="hidden sm:inline-block truncate max-w-[10rem] md:max-w-[14rem] lg:max-w-[22rem] xl:max-w-md font-mono text-xs uppercase tracking-wider text-gray-500"
            >
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

            <div className="relative group">
              <button
                type="button"
                className="text-right cursor-pointer"
                aria-haspopup="menu"
              >
                <div className="font-mono text-xs text-gray-600">sessão</div>
                <div
                  title={
                    user?.empresa?.nome || user?.first_name || user?.username
                  }
                  className="text-sm text-black max-w-40 lg:max-w-56 truncate group-hover:underline underline-offset-4 decoration-gray-400"
                >
                  {user?.empresa?.nome || user?.first_name || user?.username}
                </div>
              </button>

              <div className="absolute right-0 top-full z-20 hidden pt-2 group-hover:block group-focus-within:block">
                <div
                  role="menu"
                  className="w-48 border border-gray-200 bg-white shadow-sm py-1"
                >
                  <Link
                    to="/empresa"
                    role="menuitem"
                    className="block px-4 py-2 text-sm text-gray-600 hover:text-black hover:bg-gray-50 transition-colors"
                  >
                    Dados da empresa
                  </Link>
                  <Link
                    to="/alterar-senha"
                    role="menuitem"
                    className="block px-4 py-2 text-sm text-gray-600 hover:text-black hover:bg-gray-50 transition-colors"
                  >
                    Alterar senha
                  </Link>
                  <div className="my-1 border-t border-gray-200" />
                  <button
                    type="button"
                    role="menuitem"
                    onClick={() => logout()}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:text-black hover:bg-gray-50 transition-colors"
                  >
                    Sair
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
