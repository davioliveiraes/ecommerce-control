import { useEffect, useRef } from 'react'
import type { CustomCellEditorProps } from 'ag-grid-react'

function parseLocaleNumber(raw: string): number | null {
  const trimmed = raw.trim()
  if (trimmed === '') return null
  const hasComma = trimmed.includes(',')
  const hasDot = trimmed.includes('.')
  let normalized = trimmed
  if (hasComma && hasDot) {
    normalized = trimmed.replace(/\./g, '').replace(',', '.')
  } else if (hasComma) {
    normalized = trimmed.replace(',', '.')
  }
  const num = parseFloat(normalized)
  return isNaN(num) ? null : num
}

function initialFromValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return ''
  const num = parseFloat(String(value))
  if (isNaN(num)) return ''
  return num.toFixed(2).replace('.', ',')
}

/**
 * Editor de célula para preços (AG Grid 35, API funcional).
 *
 * Usa input NÃO-CONTROLADO (defaultValue + ref) para que os re-renders que o
 * AG Grid dispara a cada onValueChange não atrapalhem a digitação. O valor
 * confirmado no Enter é o último número passado a onValueChange (o grid o lê
 * via getValue). Aceita vírgula ou ponto como separador decimal.
 * Enter confirma, Esc cancela.
 */
export function MoneyCellEditor({ value, onValueChange }: CustomCellEditorProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const el = inputRef.current
    if (el) {
      el.focus()
      el.select()
    }
  }, [])

  const handleChange = (raw: string) => {
    onValueChange(parseLocaleNumber(raw))
  }

  return (
    <input
      ref={inputRef}
      type="text"
      inputMode="decimal"
      defaultValue={initialFromValue(value)}
      onChange={(e) => handleChange(e.target.value)}
      className="ecommerce-cell-editor"
    />
  )
}
