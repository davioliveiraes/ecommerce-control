import { z } from 'zod'

const decimalString = z
  .string()
  .min(1, 'Obrigatório')
  .refine((value) => !isNaN(parseFloat(value)) && parseFloat(value) > 0, {
    message: 'Informe um valor maior que zero',
  })

export const lancamentoFinanceiroSchema = z.object({
  descricao: z.string().min(1, 'Descrição é obrigatória').max(255),
  tipo: z.enum(['CUSTO', 'RECEITA', 'DESPESA']),
  categoria_id: z.number().nullable(),
  valor: decimalString,
  data_lancamento: z.string().min(1, 'Data é obrigatória'),
  status: z.enum(['PENDENTE', 'PAGO']),
  observacoes: z.string(),
})

export type LancamentoFinanceiroForm = z.infer<
  typeof lancamentoFinanceiroSchema
>
