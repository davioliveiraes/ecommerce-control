# Arquitetura

Documento técnico sobre como o projeto está organizado, por que algumas decisões foram tomadas e como os pedaços conversam entre si. Voltado para quem vai contribuir ou estudar a base de código.

> Visão de alto nível: monólito modular Django no backend, SPA React no frontend, ambos isolados em containers e conversando exclusivamente por HTTP JSON com autenticação via bearer token.

---

## 1. Visão geral em uma imagem

```
                    ┌─────────────────────┐
                    │  Browser (React SPA)│
                    │  - Tailwind          │
                    │  - TanStack Query    │
                    │  - AG Grid           │
                    └──────────┬──────────┘
                               │  fetch + Bearer token
                               ▼
                    ┌─────────────────────┐
                    │   Django + Ninja    │
                    │  /api/* (REST-like) │
                    │  /admin (built-in)  │
                    └──────────┬──────────┘
                               │  Django ORM
                               ▼
                    ┌─────────────────────┐
                    │   PostgreSQL 16     │
                    └─────────────────────┘
```

Tudo orquestrado por `docker-compose.yml`: 3 containers (`db`, `backend`, `frontend`), volumes locais para hot-reload em ambos os lados.

## 2. Backend — Django + Ninja

### 2.1 Apps internas

Cada app tem responsabilidade única e fronteira clara:

| App | Responsabilidade |
|---|---|
| `catalog` | Marcas, categorias, subcategorias, produtos, variações. SKUs e EANs. |
| `finance` | Categorias financeiras, lançamentos, dashboards consolidados, mock de analytics. |
| `importer` | Comando de importação por planilha (xlsx) — para popular catálogo a partir de Excel/Sheets. |
| `reports` | Geração de PDFs com ReportLab. Não tem modelo próprio — só consome dados de outras apps. |

Cada app segue a mesma estrutura interna:

```
apps/<nome>/
├── models/         # um modelo por arquivo
├── routers/        # endpoints Ninja, agrupados por recurso
├── schemas/        # Pydantic input/output (DTOs)
├── services/       # lógica de negócio reutilizável
├── tests/          # pytest + Django TestCase
├── admin.py        # ModelAdmin
└── management/commands/   # seeds e tarefas batch
```

### 2.2 Por que Django Ninja

- API tipada estilo FastAPI, mas reusando o Django ORM, admin e auth — sem precisar de DRF.
- Schemas Pydantic geram OpenAPI automaticamente em `/api/docs`.
- Funções simples em vez de classes — menos cerimônia que ViewSets.

### 2.3 Autenticação

Bearer token assinado (`django.core.signing`) com TTL configurável em `AUTH_TOKEN_MAX_AGE_SECONDS` (default 12h). Sem sessões HTTP, sem CSRF — adequado para SPA + API stateless.

Fluxo: `POST /api/auth/login { username, password }` retorna `{ token, user }`. O frontend guarda o token em `localStorage` e envia em todas as requisições subsequentes.

### 2.4 Modelos centrais

Hierarquia do catálogo:

```
Marca ──┐
        ├── Produto ── Variação (SKU)
Categoria ── Subcategoria ──┘
```

Hierarquia financeira:

```
CategoriaFinanceira (RECEITA | CUSTO | DESPESA)
    └── LancamentoFinanceiro (com data, valor, status, forma_pagamento, parcelas...)
```

Variação tem campos calculados como properties (não no banco):

- `margem_decimal` e `margem_percentual` (sobre `preco_site`).
- `margem_promocional_decimal` e `margem_promocional_percentual` (sobre `preco_promocional`).

### 2.5 Mock determinístico de analytics

`finance/services/analytics_service.py` simula estatísticas estilo Nuvemshop (visitas, conversões, rankings de produto) usando `random.Random(42)`. A semente fixa garante:

- Números reprodutíveis em qualquer ambiente.
- Coerência entre runs (top produto não muda entre reloads).
- Plotagem visualmente convincente em screenshots.

Os schemas em `finance/routers/analytics.py` definem o **contrato**. Para conectar à API real do Nuvemshop, basta reescrever o service mantendo o mesmo retorno — o frontend não muda.

## 3. Frontend — React + Vite

### 3.1 Camadas

```
src/
├── api/         # axios clients + fetchers (1 arquivo por recurso)
├── types/       # interfaces TS espelhando schemas Pydantic
├── hooks/       # custom hooks (useDocumentTitle, useDownloadPdf...)
├── components/  # componentes apresentacionais + de domínio
├── pages/       # rotas top-level (1 por rota)
└── contexts/    # AuthContext apenas
```

Sem Redux/Zustand. Estado de servidor fica no TanStack Query; estado de UI fica em `useState` local. Auth é o único state global.

### 3.2 Por que sem Recharts/Chart.js

Os gráficos do dashboard (linha temporal, donut, barras horizontais, barras verticais, sparkline) são SVG cru, ~100-200 linhas cada. Vantagens:

- **Bundle menor**: economiza ~150KB gzip.
- **Controle visual total**: paleta exata, tooltips customizados, animações específicas.
- **Tooltips React**: nada de `<title>` SVG nativo (delay do browser + estilo limitado). Cada chart tem hover via `useState` + overlay absoluto.

Os 5 componentes de gráfico:

- `TimelineChart.tsx` — linha SVG com flip automático de tooltip nos pontos do topo.
- `CategoryPieChart.tsx` — donut + painel de filtros lateral.
- `PaymentStatisticsPanel.tsx` — barras verticais agrupadas.
- `StoreOverviewPanel.tsx` — barras verticais simples (revenue por mês).
- `MiniSparkline.tsx` — mini linha + área para KPI cards.

### 3.3 AG Grid no catálogo

Catálogo usa AG Grid Community por causa do agrupamento de variações por produto (row grouping) + virtualização nativa para listas grandes. Configuração relevante em `frontend/src/components/catalogo/CatalogoGrid.tsx`:

- `rowGroup: true` em `descricao_site_group` (agrupa variações pelo produto pai).
- `quickFilterText` para busca em todas as colunas.
- Cell renderers customizados por tipo (preço, percentual, status badge, ações).

### 3.4 Formulários

`React Hook Form` + `Zod`:

- Schema Zod por formulário (`schemas/produtoSchema.ts`, etc).
- `zodResolver` integra validação no submit.
- Erros campo-a-campo via `formState.errors`.

## 4. Relatórios PDF

`apps/reports` usa ReportLab. Cada relatório tem:

1. Um **router** (`routers/<nome>.py`) que recebe os filtros e retorna `FileResponse`.
2. Um **service** (`services/<nome>_report.py`) que monta o PDF.
3. Helpers compartilhados em `services/pdf_base.py` (cabeçalho, footer, fonts, paleta).

Padrão de layout:

```
┌──────────────────────────────────────┐
│  Cabeçalho com kicker + título       │
│  Faixa de filtros aplicados          │
├──────────────────────────────────────┤
│  KPIs em cards horizontais           │
├──────────────────────────────────────┤
│  Gráficos auxiliares (opcional)      │
├──────────────────────────────────────┤
│  Tabela principal com paginação      │
└──────────────────────────────────────┘
```

A geração é **streaming**: o response é entregue assim que o `Canvas` é salvo, sem buffer intermediário.

### Modal de exportação

`frontend/src/components/reports/ExportPdfModal.tsx` é um modal reutilizável que recebe:

- `colunasDisponiveis`: lista de `{ id, label }`.
- `filtrosExtras`: JSX opcional para filtros específicos do relatório (ex.: "apenas promocionais").
- `onConfirm(colunas)`: callback com as colunas selecionadas.

O download em si é abstraído pelo hook `useDownloadPdf()`.

## 5. Fluxo de dados típico

Exemplo: usuário aplica filtro de data no dashboard financeiro.

```
[Browser] DashboardFilters muda dataInicio
     │
     ▼
[React] useState atualiza → queryKey muda
     │
     ▼
[TanStack Query] dispara fetchFinanceDashboard()
     │
     ▼
[Axios] GET /api/finance/dashboard?data_inicio=...
     │  Authorization: Bearer <token>
     ▼
[Django Ninja] router resolve schema, chama service
     │
     ▼
[Django ORM] agrega LancamentoFinanceiro (group by + sum)
     │
     ▼
[PostgreSQL] retorna rows agregadas
     │
     ▼
[Django Ninja] serializa via Pydantic schema → JSON
     │
     ▼
[TanStack Query] cacheia + entrega aos componentes
     │
     ▼
[React] KpiCards, TimelineChart, CategoryPieChart re-renderizam
```

Tempo médio observado em dev (Docker local com seed completo): ~80-120ms por request.

## 6. Convenções de código

### Backend

- **Tipos**: type hints em tudo (Pydantic + Python 3.11 generics).
- **Imports**: `from finance.models import ...` (a pasta `backend/apps` está no PYTHONPATH).
- **Migrations**: nunca editar uma migration já aplicada em desenvolvimento compartilhado.
- **Comentários docstring**: apenas quando o que é não-óbvio. Funções pequenas com nome bom não precisam.

### Frontend

- **Componente = um arquivo**. Nome em PascalCase. Sem `index.ts` re-export.
- **Tailwind direto**. Sem CSS modules, sem styled-components. Quando precisa de composição, usa `clsx`-like (`${} ${}`).
- **Sem comentários explicando o quê**. O código bem nomeado serve. Só comente o porquê.

## 7. Testes

Backend: pytest + Django TestCase. Cobertura focada em:

- Serviços críticos (cálculo de margens, agregações de dashboard).
- Endpoints de catálogo e finance.
- Geração de PDF (smoke test que confere bytes válidos).

Rodar:

```bash
docker exec ecommerce_backend pytest
```

Frontend: ainda não tem suíte automatizada — está no roadmap (Vitest + Testing Library).

## 8. Decisões que foram consideradas e descartadas

| Considerado | Por que descartado |
|---|---|
| DRF | Mais cerimônia que Ninja para a mesma necessidade. |
| Next.js | SSR não traz benefício para painel autenticado. |
| Recharts | Bundle grande + tooltip nativo sutil. |
| Storybook | Custo de manutenção alto para o escopo atual. |
| GraphQL | Endpoints REST resolvem com schemas Pydantic; sem clientes múltiplos consumindo. |
| Celery | Sem tarefas assíncronas hoje; geração de PDF é fast o suficiente síncrona. |

---

Para reabrir qualquer uma dessas decisões, edite este documento junto com a PR — o histórico vira parte do raciocínio.
