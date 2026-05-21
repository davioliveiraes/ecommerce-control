import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { to: '/', label: 'Início' },
  { to: '/catalogo', label: 'Catálogo' },
  { to: '/finance', label: 'Finance' },
]

export function Topbar() {
  const { pathname } = useLocation()

  return (
    <header className="border-b border-gray-200 bg-white/85 backdrop-blur sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-8 h-16 flex items-center justify-between">
        <Link to="/" aria-label="Ir para a página inicial" className="flex items-center">
          <img src="/brand/logo_ibeize.png" alt="Ibeize" className="h-9 w-auto" />
        </Link>

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
                  <span className="absolute left-3 right-3 bottom-0 h-[2px] bg-orange" />
                )}
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
