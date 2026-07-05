import { isAxiosError } from 'axios'

export function mensagemDeErro(err: unknown, fallback: string): string {
  if (isAxiosError(err)) {
    const detail = (err.response?.data as { detail?: unknown } | undefined)
      ?.detail
    if (typeof detail === 'string') return detail
    // Erros de validação do Ninja (422): lista de {msg, ...}
    if (Array.isArray(detail) && detail.length > 0) {
      const primeiro = detail[0] as { msg?: string }
      if (typeof primeiro.msg === 'string')
        return primeiro.msg.replace(/^Value error,\s*/, '')
    }
  }
  return fallback
}
