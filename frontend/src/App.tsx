import {
  createBrowserRouter,
  RouterProvider,
  Outlet,
  Navigate,
  useParams,
} from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import { Topbar } from './components/Topbar'
import { HomePage } from './pages/HomePage'
import { CatalogoPage } from './pages/CatalogoPage'
import { ProdutoEditorPage } from './pages/ProdutoEditorPage'
import { VariacaoRedirect } from './pages/VariacaoRedirect'
import { FinancePage } from './pages/FinancePage'
import { LancamentosFinanceirosPage } from './pages/LancamentosFinanceirosPage'
import { LancamentoFinanceiroEditorPage } from './pages/LancamentoFinanceiroEditorPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      retry: 1,
    },
  },
})

function RootLayout() {
  return (
    <div className="min-h-full flex flex-col">
      <Topbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}

function LegacyProdutoRedirect() {
  const { id } = useParams<{ id: string }>()
  return <Navigate to={`/catalogo/produto/${id}`} replace />
}

const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/catalogo', element: <CatalogoPage /> },
      { path: '/catalogo/produto/:id', element: <ProdutoEditorPage /> },
      {
        path: '/catalogo/produtos/:id/editar',
        element: <LegacyProdutoRedirect />,
      },
      { path: '/catalogo/variacao/:id', element: <VariacaoRedirect /> },
      { path: '/finance', element: <FinancePage /> },
      { path: '/finance/lancamentos', element: <LancamentosFinanceirosPage /> },
      {
        path: '/finance/lancamentos/novo',
        element: <LancamentoFinanceiroEditorPage />,
      },
      {
        path: '/finance/lancamentos/:id/editar',
        element: <LancamentoFinanceiroEditorPage />,
      },
    ],
  },
])

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  )
}

export default App
