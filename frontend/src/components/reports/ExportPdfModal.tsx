import { useState, type ReactNode } from 'react'
import { useAuth } from '../../hooks/useAuth'
import type { ColunaRelatorio } from '../../types/reports'

interface Props {
  isOpen: boolean
  onClose: () => void
  titulo: string
  colunasDisponiveis: ColunaRelatorio[]
  filtrosExtras?: ReactNode
  onConfirm: (colunasSelecionadas: string[]) => Promise<void>
  isDownloading: boolean
}

export function ExportPdfModal({
  isOpen,
  onClose,
  titulo,
  colunasDisponiveis,
  filtrosExtras,
  onConfirm,
  isDownloading,
}: Props) {
  const { user } = useAuth()
  const nomeEmpresa = user?.empresa?.nome || ''
  const [colunasSelecionadas, setColunasSelecionadas] = useState<Set<string>>(
    new Set(
      colunasDisponiveis
        .filter((coluna) => coluna.selecionadaPorPadrao)
        .map((coluna) => coluna.chave),
    ),
  )

  if (!isOpen) return null

  const toggleColuna = (chave: string) => {
    const proximo = new Set(colunasSelecionadas)
    if (proximo.has(chave)) {
      proximo.delete(chave)
    } else {
      proximo.add(chave)
    }
    setColunasSelecionadas(proximo)
  }

  const handleConfirm = async () => {
    if (colunasSelecionadas.size === 0) {
      window.alert('Selecione pelo menos uma coluna.')
      return
    }
    await onConfirm(Array.from(colunasSelecionadas))
  }

  // Overlay em preto literal: bg-black remapeia para claro no tema dark
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#000]/45 p-4">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-200 bg-white shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-gray-200 px-6 py-4">
          <div>
            <div className="kicker mb-1">
              Controle Interno{nomeEmpresa ? ` — ${nomeEmpresa}` : ''}
            </div>
            <h2 className="font-display text-xl font-semibold text-black">
              {titulo}
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-8 w-8 items-center justify-center border border-gray-200 text-gray-600 hover:border-black hover:text-black transition-colors disabled:opacity-50"
            aria-label="Fechar"
            disabled={isDownloading}
          >
            <IconClose />
          </button>
        </div>

        {filtrosExtras && (
          <div className="border-b border-gray-200 px-6 py-4">
            <h3 className="mb-3 text-sm font-medium text-black">Filtros</h3>
            {filtrosExtras}
          </div>
        )}

        <div className="px-6 py-4">
          <h3 className="mb-3 text-sm font-medium text-black">
            Colunas no relatório ({colunasSelecionadas.size} selecionada
            {colunasSelecionadas.size === 1 ? '' : 's'})
          </h3>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {colunasDisponiveis.map((coluna) => (
              <label
                key={coluna.chave}
                className="flex min-h-10 cursor-pointer items-center gap-2 border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:border-black hover:bg-gray-50 transition-colors"
              >
                <input
                  type="checkbox"
                  checked={colunasSelecionadas.has(coluna.chave)}
                  onChange={() => toggleColuna(coluna.chave)}
                  className="accent-black"
                />
                <span>{coluna.label}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-2 border-t border-gray-200 px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            disabled={isDownloading}
            className="px-4 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={isDownloading || colunasSelecionadas.size === 0}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <IconDownload />
            {isDownloading ? 'Gerando PDF...' : 'Gerar PDF'}
          </button>
        </div>
      </div>
    </div>
  )
}

function IconClose() {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  )
}

function IconDownload() {
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
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <path d="M7 10l5 5 5-5" />
      <path d="M12 15V3" />
    </svg>
  )
}
