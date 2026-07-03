import { useEffect, type ReactNode } from 'react'

interface Props {
  isOpen: boolean
  title: string
  description?: ReactNode
  kicker?: string
  confirmLabel: string
  cancelLabel?: string
  isPending?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  isOpen,
  title,
  description,
  kicker = 'Controle Interno',
  confirmLabel,
  cancelLabel = 'Voltar',
  isPending = false,
  onConfirm,
  onCancel,
}: Props) {
  useEffect(() => {
    if (!isOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isPending) onCancel()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [isOpen, isPending, onCancel])

  if (!isOpen) return null

  // Overlay em preto literal: bg-black remapeia para claro no tema dark
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#000]/45 p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget && !isPending) onCancel()
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        className="w-full max-w-md border border-gray-200 bg-white shadow-2xl"
      >
        <div className="px-6 py-5">
          <div className="kicker mb-2">{kicker}</div>
          <h2 className="font-display text-xl font-semibold text-black mb-2">
            {title}
          </h2>
          {description && (
            <div className="text-sm text-gray-600 leading-relaxed">
              {description}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 border-t border-gray-200 px-6 py-4">
          <button
            type="button"
            onClick={onCancel}
            disabled={isPending}
            className="px-4 py-2 text-sm border border-gray-200 bg-white text-black hover:border-gray-400 transition-colors disabled:opacity-50"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isPending}
            className="px-4 py-2 text-sm border border-black bg-black text-white hover:bg-gray-900 hover:border-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? 'Processando...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
