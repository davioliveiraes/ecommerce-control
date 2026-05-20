import { useParams, Navigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { fetchVariacao } from '../api/variacoes'

export function VariacaoRedirect() {
  const { id } = useParams<{ id: string }>()
  const variacaoId = Number(id)

  const { data, isLoading, isError } = useQuery({
    queryKey: ['variacao-redirect', variacaoId],
    queryFn: () => fetchVariacao(variacaoId),
    enabled: !!variacaoId && !isNaN(variacaoId),
  })

  if (isLoading) {
    return (
      <div className="text-center py-16 font-mono text-sm text-gray-600">
        redirecionando...
      </div>
    )
  }
  if (isError || !data) {
    return <Navigate to="/catalogo" replace />
  }
  return <Navigate to={`/catalogo/produto/${data.produto_id}`} replace />
}
