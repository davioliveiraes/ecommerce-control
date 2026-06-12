import { useState } from 'react'

interface Props {
  source: string
  endpoints: Array<{ method: string; path: string; descricao: string }>
}

export function DemoDataBanner({ source, endpoints }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <aside className="border border-black bg-gray-50">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center border border-black bg-white">
          <IconInfo />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center border border-black bg-black px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-white">
              Demo
            </span>
            <span className="text-sm font-medium text-black">
              Dados de demonstração — gerados deterministicamente no backend.
            </span>
          </div>
          <p className="mt-0.5 text-xs text-gray-600">
            No ambiente real, estes valores virão da{' '}
            <strong className="text-black">{source}</strong>. Clique para ver
            como fazer essa integração.
          </p>
        </div>
        <span className="font-mono text-xs text-gray-600">
          {expanded ? 'fechar' : 'detalhes'}
        </span>
      </button>

      {expanded && (
        <div className="border-t border-black bg-white px-4 py-4 text-sm text-gray-700">
          <h4 className="font-display text-sm font-semibold text-black mb-2">
            Como ligar dados reais
          </h4>
          <ol className="list-decimal space-y-1.5 pl-5 text-xs text-gray-700">
            <li>
              Cadastre uma aplicação em{' '}
              <code className="font-mono text-[11px]">
                partners.nuvemshop.com.br
              </code>
              , obtenha <code className="font-mono text-[11px]">client_id</code>{' '}
              /{' '}
              <code className="font-mono text-[11px]">client_secret</code> e
              rode o OAuth code-grant para trocar o{' '}
              <code className="font-mono text-[11px]">code</code> da loja por
              um <code className="font-mono text-[11px]">access_token</code>{' '}
              persistente.
            </li>
            <li>
              No backend, troque o serviço{' '}
              <code className="font-mono text-[11px]">
                finance/services/analytics_service.py
              </code>{' '}
              por chamadas à API real, preservando os schemas em{' '}
              <code className="font-mono text-[11px]">
                finance/routers/analytics.py
              </code>{' '}
              (o frontend não muda).
            </li>
            <li>
              Toda chamada precisa de{' '}
              <code className="font-mono text-[11px]">
                Authentication: bearer &lt;token&gt;
              </code>{' '}
              e{' '}
              <code className="font-mono text-[11px]">
                User-Agent: App (contato@dominio)
              </code>
              . Sem User-Agent, retorna 400.
            </li>
            <li>
              Respeite o rate limit (40 req de bucket, 2 req/s) e a paginação
              via <code className="font-mono text-[11px]">page</code> /{' '}
              <code className="font-mono text-[11px]">per_page</code> (máx.
              200). Métricas de visita/conversão{' '}
              <em>não existem</em> na API — plugue GA4 ou Plausible.
            </li>
          </ol>

          <h4 className="font-display text-sm font-semibold text-black mt-4 mb-2">
            Endpoints Nuvemshop equivalentes
          </h4>
          <div className="overflow-hidden border border-gray-200">
            <table className="w-full text-xs">
              <thead className="bg-gray-50 text-left">
                <tr>
                  <th className="px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-gray-600">
                    Método
                  </th>
                  <th className="px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-gray-600">
                    Path
                  </th>
                  <th className="px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-gray-600">
                    Uso
                  </th>
                </tr>
              </thead>
              <tbody>
                {endpoints.map((e, idx) => (
                  <tr
                    key={idx}
                    className="border-t border-gray-100"
                  >
                    <td className="px-3 py-2 font-mono text-[11px] font-semibold text-black">
                      {e.method}
                    </td>
                    <td className="px-3 py-2 font-mono text-[11px] text-black">
                      {e.path}
                    </td>
                    <td className="px-3 py-2 text-gray-700">{e.descricao}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p className="mt-3 font-mono text-[11px] text-gray-600">
            Documentação oficial:{' '}
            <span className="text-black">tiendanube.github.io/api-documentation</span>{' '}
            · Guia de integração passo a passo em{' '}
            <code className="text-[11px]">docs/INTEGRACAO_NUVEMSHOP.md</code>.
          </p>
        </div>
      )}
    </aside>
  )
}

function IconInfo() {
  return (
    <svg
      width="12"
      height="12"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="9" />
      <line x1="12" y1="8" x2="12" y2="8" />
      <line x1="12" y1="11" x2="12" y2="16" />
    </svg>
  )
}
