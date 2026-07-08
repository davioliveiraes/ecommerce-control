import { z } from 'zod'

const decimalString = z
  .string()
  .min(1, 'Obrigatório')
  .refine((v) => !isNaN(parseFloat(v)) && parseFloat(v) >= 0, {
    message: 'Valor inválido',
  })

const decimalStringOpcional = z
  .union([z.string(), z.null()])
  .refine(
    (v) =>
      v === null ||
      v === '' ||
      (!isNaN(parseFloat(v as string)) && parseFloat(v as string) >= 0),
    { message: 'Valor inválido' },
  )
  .transform((v) => (v === '' ? null : v))

// Obrigatório, mas mantém o tipo `string | null` para aceitar null vindo de
// dados antigos no carregamento do form; na validação exige número >= 0.
const decimalStringObrigatorio = z
  .union([z.string(), z.null()])
  .refine(
    (v) =>
      v !== null &&
      v !== '' &&
      !isNaN(parseFloat(v)) &&
      parseFloat(v) >= 0,
    { message: 'Obrigatório' },
  )

export const variacaoSchema = z.object({
  id: z.number().optional(),
  sku_nuvemshop: z.string().max(50, 'Máximo 50 caracteres'),
  id_gestaoclick: z.string().max(50),
  codigo_barras: z.string().max(50),
  descricao: z.string().max(500),
  custo: decimalString,
  preco_loja: decimalString,
  preco_site: decimalStringObrigatorio,
  preco_promocional: decimalStringOpcional,
  status_nuvemshop: z.enum(['ATIVO', 'INATIVO']),
  status_integracao: z.enum(['ATIVO', 'INATIVO']),
  ativo: z.boolean(),
})

export const produtoEditorSchema = z.object({
  nome_gestaoclick: z.string().max(255),
  nome_site: z.string().max(255),
  descricao_produto_gestaoclick: z.string(),
  descricao_produto_site: z.string().min(1, 'Descrição do site é obrigatória'),
  categoria_id: z.number().nullable(),
  subcategoria_id: z.number().nullable(),
  variacoes: z
    .array(variacaoSchema)
    .min(1, 'Pelo menos uma variação é obrigatória'),
})

export type ProdutoEditorForm = z.infer<typeof produtoEditorSchema>
export type VariacaoForm = z.infer<typeof variacaoSchema>
