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
  forma_pagamento: z.enum([
    '',
    'PIX',
    'CARTAO_CREDITO',
    'BOLETO',
    'NUVEMPAGO',
    'OUTRO',
  ]),
  meio_pagamento: z.enum([
    '',
    'NUVEMPAGO',
    'MERCADO_PAGO',
    'PAGSEGURO',
    'MANUAL',
    'OUTRO',
  ]),
  quantidade_parcelas: z.number().int().positive().nullable(),
  quantidade_vendas: z.number().int().positive(),
  fonte_trafego: z.string().max(100),
  observacoes: z.string(),
})

export type LancamentoFinanceiroForm = z.infer<
  typeof lancamentoFinanceiroSchema
>
