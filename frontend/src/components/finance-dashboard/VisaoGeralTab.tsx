import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import {
  createVisaoGeralPeriodo,
  deleteVisaoGeralPeriodo,
  fetchVisaoGeralPeriodos,
  updateVisaoGeralPeriodo,
} from '../../api/visaoGeral'
import type {
  VisaoGeralPeriodo,
  VisaoGeralPeriodoInput,
} from '../../types/visaoGeral'
import { formatCurrency, formatPercent } from '../../utils/format'
import { PeriodoMesAnoFilter } from './PeriodoMesAnoFilter'
import { MiniSparkline, type SparkFormato } from './MiniSparkline'
import { VisaoGeralPeriodoForm } from './VisaoGeralPeriodoForm'

interface VisaoGeralTabProps {
  ano: number
  /** mes = 0-11, ou null para "Ano inteiro". */
  mes: number | null
  anos: number[]
  onAnoChange: (ano: number) => void
  onMesChange: (mes: number | null) => void
  onClear: () => void
  dataInicio: string
  dataFim: string
}

interface BehaviorItem {
  label: string
  valor: number
}

interface ModalState {
  open: boolean
  editing: VisaoGeralPeriodo | null
}

const TOTAIS_ZERADOS = {
  visitas: 0,
  visualizacoes_categoria: 0,
  visualizacoes_produto: 0,
  carrinhos_criados: 0,
  checkout_iniciado: 0,
  checkout_entrega: 0,
  checkout_pagamento: 0,
  pedidos_criados: 0,
  pedidos_pagos: 0,
  receita: 0,
}

export function VisaoGeralTab({
  ano,
  mes,
  anos,
  onAnoChange,
  onMesChange,
  onClear,
  dataInicio: filtroInicio,
  dataFim: filtroFim,
}: VisaoGeralTabProps) {
  const queryClient = useQueryClient()
  const [modal, setModal] = useState<ModalState>({ open: false, editing: null })

  const query = useQuery({
    queryKey: ['visao-geral-periodos'],
    queryFn: fetchVisaoGeralPeriodos,
  })

  const periodos = query.data ?? []
  const periodosFiltrados = useMemo(
    () =>
      periodos.filter(
        (p) =>
          (!filtroInicio || p.data_fim >= filtroInicio) &&
          (!filtroFim || p.data_inicio <= filtroFim),
      ),
    [periodos, filtroInicio, filtroFim],
  )

  // Ordem cronológica (mais antigo → mais recente) para o sparkline de tendência.
  const cronologico = useMemo(
    () => [...periodosFiltrados].reverse(),
    [periodosFiltrados],
  )
  const labels = cronologico.map((p) => shortDate(p.data_fim))

  // Totais do intervalo selecionado (início → fim).
  const totais = useMemo(
    () =>
      periodosFiltrados.reduce(
        (acc, p) => ({
          visitas: acc.visitas + p.visitas,
          visualizacoes_categoria:
            acc.visualizacoes_categoria + p.visualizacoes_categoria,
          visualizacoes_produto:
            acc.visualizacoes_produto + p.visualizacoes_produto,
          carrinhos_criados: acc.carrinhos_criados + p.carrinhos_criados,
          checkout_iniciado: acc.checkout_iniciado + p.checkout_iniciado,
          checkout_entrega: acc.checkout_entrega + p.checkout_entrega,
          checkout_pagamento: acc.checkout_pagamento + p.checkout_pagamento,
          pedidos_criados: acc.pedidos_criados + p.pedidos_criados,
          pedidos_pagos: acc.pedidos_pagos + p.pedidos_pagos,
          receita: acc.receita + (parseFloat(p.receita) || 0),
        }),
        { ...TOTAIS_ZERADOS },
      ),
    [periodosFiltrados],
  )

  const vendas = totais.pedidos_pagos
  const ticketMedio = vendas ? totais.receita / vendas : 0
  const convVisitasVendas = totais.visitas
    ? (vendas / totais.visitas) * 100
    : 0
  const convVisitasCarrinhos = totais.visitas
    ? (totais.carrinhos_criados / totais.visitas) * 100
    : 0
  const convCheckoutsVendas = totais.checkout_iniciado
    ? (vendas / totais.checkout_iniciado) * 100
    : 0

  // Editar/Excluir operam sobre o período mais recente dentro do filtro aplicado.
  const maisRecente = periodosFiltrados[0] ?? null
  const temDados = periodosFiltrados.length > 0

  const invalidar = () =>
    queryClient.invalidateQueries({ queryKey: ['visao-geral-periodos'] })

  const createMutation = useMutation({
    mutationFn: (payload: VisaoGeralPeriodoInput) =>
      createVisaoGeralPeriodo(payload),
    onSuccess: () => {
      invalidar()
      setModal({ open: false, editing: null })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: VisaoGeralPeriodoInput }) =>
      updateVisaoGeralPeriodo(id, payload),
    onSuccess: () => {
      invalidar()
      setModal({ open: false, editing: null })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteVisaoGeralPeriodo(id),
    onSuccess: () => invalidar(),
  })

  const handleSubmit = (payload: VisaoGeralPeriodoInput) => {
    if (modal.editing) {
      updateMutation.mutate({ id: modal.editing.id, payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  const handleDelete = () => {
    if (!maisRecente) return
    if (
      !window.confirm(
        `Excluir o período ${maisRecente.label_periodo}? Esta ação remove o registro da visão geral.`,
      )
    )
      return
    deleteMutation.mutate(maisRecente.id)
  }

  if (query.isLoading) {
    return (
      <div className="border border-gray-200 bg-white px-6 py-16 text-center font-mono text-sm text-gray-600">
        carregando visão geral...
      </div>
    )
  }

  if (query.isError) {
    return (
      <div className="border border-gray-300 bg-gray-50 px-6 py-5">
        <div className="kicker mb-2">Erro</div>
        <h3 className="font-display text-lg font-semibold text-black mb-1">
          Falha ao carregar a visão geral
        </h3>
        <p className="text-sm text-gray-600">
          {(query.error as Error)?.message || 'Erro desconhecido'}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <div className="kicker">Estatísticas</div>
          <h2 className="font-display text-2xl font-semibold text-black">
            Visão geral
          </h2>
          <p className="text-sm text-gray-600">
            Dados provenientes das informações do NuvemShop.
          </p>
        </div>

        <div className="flex flex-wrap items-end justify-between gap-3 border border-gray-200 bg-gray-50 px-4 py-3">
          <PeriodoMesAnoFilter
            ano={ano}
            mes={mes}
            anos={anos}
            onAnoChange={onAnoChange}
            onMesChange={onMesChange}
            onClear={onClear}
          />

          <div className="flex flex-wrap items-center gap-2">
            {maisRecente && (
              <>
                <button
                  type="button"
                  onClick={() => setModal({ open: true, editing: maisRecente })}
                  className="inline-flex items-center gap-1.5 border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 hover:border-black hover:text-black transition-colors"
                >
                  Editar
                </button>
                <button
                  type="button"
                  onClick={handleDelete}
                  disabled={deleteMutation.isPending}
                  className="inline-flex items-center gap-1.5 border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-700 hover:border-black hover:text-black transition-colors disabled:opacity-50"
                >
                  Excluir
                </button>
              </>
            )}
            <button
              type="button"
              onClick={() => setModal({ open: true, editing: null })}
              className="inline-flex items-center gap-1.5 border border-black bg-black px-3 py-1.5 text-sm text-white hover:bg-gray-900 transition-colors"
            >
              <IconPlus />
              Adicionar período
            </button>
          </div>
        </div>
      </header>

      {periodos.length === 0 ? (
        <EmptyState onAdd={() => setModal({ open: true, editing: null })} />
      ) : !temDados ? (
        <div className="border border-dashed border-gray-300 bg-gray-50 px-6 py-12 text-center text-sm text-gray-600">
          Nenhum período dentro do intervalo selecionado. Ajuste as datas ou
          clique em “Limpar filtros”.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
            <KpiSparkCard
              label="Visitas"
              info="Total de visitas no intervalo."
              valor={totais.visitas}
              formato="inteiro"
              serie={cronologico.map((p) => p.visitas)}
              labels={labels}
              color="var(--color-black)"
            />
            <KpiSparkCard
              label="Vendas"
              info="Pedidos pagos no intervalo."
              valor={vendas}
              formato="inteiro"
              serie={cronologico.map((p) => p.vendas)}
              labels={labels}
              color="var(--color-gray-700)"
            />
            <KpiSparkCard
              label="Receita"
              info="Receita bruta dos pedidos pagos."
              valor={totais.receita}
              formato="moeda"
              serie={cronologico.map((p) => parseFloat(p.receita) || 0)}
              labels={labels}
              color="var(--color-gray-800)"
            />
            <KpiSparkCard
              label="Ticket médio"
              info="Receita dividida pelas vendas."
              valor={ticketMedio}
              formato="moeda"
              serie={cronologico.map((p) => parseFloat(p.ticket_medio) || 0)}
              labels={labels}
              color="var(--color-gray-500)"
            />
          </div>

          <div className="grid grid-cols-1 gap-3 xl:grid-cols-4">
            <div className="flex flex-col gap-3 justify-between xl:col-span-3">
              <BehaviorPanel
                title="Comportamento dos visitantes"
                info="Funil de navegação dos visitantes na loja."
                items={[
                  { label: 'Total de visitas', valor: totais.visitas },
                  {
                    label: 'Visualização de categoria',
                    valor: totais.visualizacoes_categoria,
                  },
                  {
                    label: 'Visualização de produto',
                    valor: totais.visualizacoes_produto,
                  },
                  {
                    label: 'Carrinhos criados',
                    valor: totais.carrinhos_criados,
                  },
                ]}
              />
              <BehaviorPanel
                title="Comportamento no checkout"
                info="Conversão entre etapas do checkout."
                items={[
                  {
                    label: 'Checkout iniciado',
                    valor: totais.checkout_iniciado,
                  },
                  { label: 'Etapa de entrega', valor: totais.checkout_entrega },
                  {
                    label: 'Etapa de pagamento',
                    valor: totais.checkout_pagamento,
                  },
                  { label: 'Pedidos criados', valor: totais.pedidos_criados },
                  { label: 'Pedidos pagos', valor: totais.pedidos_pagos },
                ]}
              />
            </div>

            <div className="flex flex-col gap-3 justify-between xl:col-span-1">
              <ConversionCard
                label="Visitas para vendas"
                percentual={convVisitasVendas}
                detalhe={`${vendas} pedidos pagos em ${totais.visitas} visitas`}
              />
              <ConversionCard
                label="Visitas para carrinhos"
                percentual={convVisitasCarrinhos}
                detalhe={`${totais.carrinhos_criados} carrinhos criados`}
              />
              <ConversionCard
                label="Checkouts para vendas"
                percentual={convCheckoutsVendas}
                detalhe={`${vendas} pagos em ${totais.checkout_iniciado} checkouts`}
              />
            </div>
          </div>
        </>
      )}

      <VisaoGeralPeriodoForm
        open={modal.open}
        editing={modal.editing}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        error={
          (createMutation.error as Error)?.message ||
          (updateMutation.error as Error)?.message ||
          null
        }
        onClose={() => setModal({ open: false, editing: null })}
        onSubmit={handleSubmit}
      />
    </div>
  )
}

function EmptyState({ onAdd }: { onAdd: () => void }) {
  return (
    <div className="border border-dashed border-gray-300 bg-gray-50 px-6 py-16 text-center">
      <h3 className="font-display text-lg font-semibold text-black">
        Nenhum período cadastrado
      </h3>
      <p className="mx-auto mt-1 max-w-md text-sm text-gray-600">
        Exporte um relatório na NuvemShop e registre os números do período aqui
        para acompanhar visitas, comportamento e conversões.
      </p>
      <button
        type="button"
        onClick={onAdd}
        className="mt-4 inline-flex items-center gap-1.5 border border-black bg-black px-4 py-2 text-sm text-white hover:bg-gray-900 transition-colors"
      >
        <IconPlus />
        Adicionar período
      </button>
    </div>
  )
}

function KpiSparkCard({
  label,
  info,
  valor,
  formato,
  serie,
  labels,
  color,
}: {
  label: string
  info: string
  valor: number
  formato: SparkFormato
  serie: number[]
  labels: string[]
  color: string
}) {
  const display =
    formato === 'moeda' ? formatCurrency(valor) : valor.toLocaleString('pt-BR')

  return (
    <div className="border border-gray-200 bg-white px-4 py-4">
      <div className="mb-2 flex items-center gap-1.5">
        <span className="text-sm font-medium text-black">{label}</span>
        <InfoTip text={info} />
      </div>
      <div className="font-mono text-2xl font-semibold tabular-nums text-black">
        {display}
      </div>
      <div className="mt-3">
        <MiniSparkline
          serie={serie}
          labels={labels}
          formato={formato}
          color={color}
        />
      </div>
    </div>
  )
}

function BehaviorPanel({
  title,
  info,
  items,
}: {
  title: string
  info: string
  items: BehaviorItem[]
}) {
  const max = Math.max(1, ...items.map((item) => item.valor))

  return (
    <section className="border border-gray-200 bg-white p-5">
      <div className="mb-4 flex items-center gap-1.5">
        <h3 className="font-display text-base font-semibold text-black">
          {title}
        </h3>
        <InfoTip text={info} />
      </div>

      <div className="space-y-2.5">
        {items.map((item, idx) => (
          <HorizontalBar
            key={item.label}
            label={item.label}
            value={item.valor}
            max={max}
            color={shadeFor(idx, items.length)}
          />
        ))}
      </div>
    </section>
  )
}

function HorizontalBar({
  label,
  value,
  max,
  color,
}: {
  label: string
  value: number
  max: number
  color: string
}) {
  const [isHover, setIsHover] = useState(false)
  const width = (value / max) * 100

  return (
    <div className="grid grid-cols-[140px_minmax(0,1fr)_64px] items-center gap-3 text-xs">
      <span className="truncate font-mono text-gray-600" title={label}>
        {label}
      </span>
      <div className="relative h-6 bg-gray-50">
        <div
          onMouseEnter={() => setIsHover(true)}
          onMouseLeave={() => setIsHover(false)}
          className="h-full cursor-pointer transition-[width] duration-300"
          style={{ width: `${Math.max(0.4, width)}%`, backgroundColor: color }}
        />
        {isHover && (
          <div
            className="pointer-events-none absolute z-10 -translate-y-full border border-black bg-white px-2 py-1 shadow-md"
            style={{ left: `min(${width}%, calc(100% - 130px))`, top: -4 }}
          >
            <div className="font-mono text-[10px] uppercase tracking-wider text-gray-600">
              {label}
            </div>
            <div className="font-mono text-xs font-semibold tabular-nums text-black">
              {value.toLocaleString('pt-BR')}
            </div>
          </div>
        )}
      </div>
      <span className="text-right font-mono tabular-nums text-black">
        {value.toLocaleString('pt-BR')}
      </span>
    </div>
  )
}

function ConversionCard({
  label,
  percentual,
  detalhe,
}: {
  label: string
  percentual: number
  detalhe: string
}) {
  return (
    <div className="border border-gray-200 bg-white px-4 py-4">
      <div className="mb-1 flex items-center gap-1.5">
        <span className="text-sm font-medium text-black">{label}</span>
        <InfoTip text={detalhe} />
      </div>
      <div className="font-mono text-xs uppercase tracking-wider text-gray-500">
        Conversão
      </div>
      <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-black">
        {formatPercent(percentual)}
      </div>
      <p className="mt-2 text-xs text-gray-600">{detalhe}</p>
      <div className="mt-3 h-1 bg-gray-100">
        <div
          className="h-1 bg-black"
          style={{ width: `${Math.min(100, percentual)}%` }}
        />
      </div>
    </div>
  )
}

function InfoTip({ text }: { text: string }) {
  if (!text) return null
  return (
    <span
      title={text}
      className="inline-flex h-3.5 w-3.5 cursor-help items-center justify-center rounded-full border border-gray-300 text-[9px] font-bold text-gray-500"
    >
      i
    </span>
  )
}

function IconPlus() {
  return (
    <svg
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 5v14" />
      <path d="M5 12h14" />
    </svg>
  )
}

function shadeFor(index: number, total: number) {
  const shades = [
    'var(--color-black)',
    'var(--color-gray-800)',
    'var(--color-gray-700)',
    'var(--color-gray-600)',
    'var(--color-gray-500)',
    'var(--color-gray-400)',
  ]
  if (total <= shades.length) return shades[index] || shades[shades.length - 1]
  return shades[index % shades.length]
}

function shortDate(iso: string) {
  const [, mes, dia] = iso.split('-')
  if (!mes || !dia) return iso
  return `${dia}/${mes}`
}
