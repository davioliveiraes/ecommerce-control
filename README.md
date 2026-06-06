# Ecommerce Internal Suite

> Painel administrativo full-stack para lojistas Nuvemshop — catálogo, financeiro, dashboards e relatórios em PDF, com seed de demonstração pronto pra rodar em 3 comandos.

![status](https://img.shields.io/badge/status-portf%C3%B3lio-black?style=flat-square) ![stack](https://img.shields.io/badge/stack-Django%20%2B%20React-black?style=flat-square) 

![Página inicial](docs/screenshots/01-home.png)

---

## O que é

Uma suíte de controle interno pensada para **lojistas Nuvemshop** que precisam de uma camada operacional além do painel padrão da plataforma: cadastro detalhado de produtos e variações com SKU/EAN, conciliação financeira manual, relatórios em PDF e dashboards mensais consolidados.

O repositório é um **template portfólio**: vem com seed determinístico (~30 produtos / ~80 variações de acessórios mobile/tech + 6 meses de lançamentos financeiros), paleta minimalista preto/branco e nomenclaturas neutras (`{{COMPANY_NAME}}`) prontas para serem personalizadas com sua marca.

## Stack

**Backend**

- Python 3.13 / Django 5
- Django Ninja (API tipada estilo FastAPI sobre Django)
- PostgreSQL 16
- ReportLab (geração de PDFs)

**Frontend**

- React 19 + TypeScript 5
- Vite 8
- Tailwind CSS 4 (paleta neutra customizada)
- TanStack Query (server state)
- React Hook Form + Zod (formulários tipados)
- AG Grid Community (catálogo)
- React Router 6

**Infra dev**

- Docker Compose (db + backend + frontend em um comando)

## Funcionalidades

### Módulo 01 — Catálogo

- Listagem em grid AG Grid com agrupamento por produto e variações expansíveis.
- Busca full-text e filtros por status (Nuvemshop / Integração).
- Editor de produto + variações com SKU, EAN-13, custo, preço loja/site, preço promocional, margem calculada e status duplo.
- Exportação PDF com seleção de colunas + filtro "apenas promocionais".

### Módulo 02 — Finance

Dashboard em **3 abas**:

1. **Financeiro** — KPIs (receita, custo, despesa, lucro), linha temporal mensal, donut de categorias, estatísticas de pagamento (forma, meio, parcelas) e exportação PDF.
2. **Visão geral** — Réplica do painel Nuvemshop nativo: visitas, vendas, receita e ticket médio com sparklines; funil de comportamento do visitante; funil de checkout; cartões de conversão. **Dados de demonstração** marcados com banner explícito + endpoints reais da API Nuvemshop documentados inline.
3. **Produtos** — Rankings: mais vendidos, mais visualizados, estoque crítico e margem.

### Lançamentos financeiros

CRUD completo de lançamentos (RECEITA / CUSTO / DESPESA) com categoria, forma de pagamento, meio, parcelas, status (PAGO / PENDENTE), filtros encadeados e exportação em PDF.

### Relatórios em PDF

Geração via ReportLab com cabeçalho, KPIs, gráficos auxiliares e tabelas filtradas. O modal de exportação permite escolher colunas e aplicar filtros adicionais (ex.: "apenas em promoção" no catálogo).

## Setup em 3 passos

```bash
# 1. Clone e entre na pasta
git clone <seu-fork>
cd ecommerce_internal_suite

# 2. Copie o .env de exemplo
cp .env.example .env

# 3. Suba tudo
docker compose up -d --build
```

Acesse:

| Serviço | URL | Credenciais |
|---|---|---|
| Frontend | http://localhost:5173 | `ecommerce_control` / `ecommerce` |
| API | http://localhost:8000/api | Bearer token via `/api/auth/login` |
| Django Admin | http://localhost:8000/admin | mesma do frontend |
| Postgres | localhost:5432 | `ecommerce` / `ecommerce` |

### Carregar dados de demonstração

```bash
# Catálogo: 8 marcas, 31 produtos, ~80 variações (acessórios mobile/tech)
docker exec ecommerce_backend python manage.py seed_catalog

# Finance: 6 meses de lançamentos financeiros distribuídos
docker exec ecommerce_backend python manage.py seed_finance --meses 6
```

Ambos os seeds usam `random.seed(42)` — os números gerados são **reproducíveis** em qualquer ambiente.

## Personalização

Este projeto é desenhado pra ser **forkado e rebrandeado**. O grosso da personalização está em três pontos:

### 1. Nome da loja

Os textos da UI usam o placeholder `{{COMPANY_NAME}}`. Faça um find/replace global:

```bash
grep -r "{{COMPANY_NAME}}" frontend/src backend/apps --include="*.tsx" --include="*.ts" --include="*.py"
```

### 2. Logo + favicon

Substitua `frontend/public/favicon.svg` e o componente de logo em `frontend/src/components/Topbar.tsx`.

### 3. Paleta de cores

A paleta neutra está em `frontend/src/index.css` e classes Tailwind padrão (`black`, `gray-*`). Mudanças centralizadas no `tailwind.config.js`.

### 4. Categorias financeiras

As categorias padrão são minimalistas e neutras (Vendas, Mercadorias, Marketing, Infra, Operacional...). Edite o seed em `backend/apps/finance/management/commands/seed_finance.py` para refletir seu negócio.

### 5. Catálogo de produtos

O seed atual gera acessórios mobile/tech. Para outro nicho:

- Edite `backend/apps/catalog/management/commands/seed_catalog.py` (marcas, categorias, produtos-base).
- OU use o importador via planilha: `backend/apps/importer/management/commands/importar_planilha.py`.

## Estrutura do projeto

```
ecommerce_internal_suite/
├── backend/
│   ├── apps/
│   │   ├── catalog/        # marcas, categorias, produtos, variações
│   │   ├── finance/        # categorias financeiras, lançamentos, dashboards, analytics mock
│   │   ├── importer/       # importação via planilha
│   │   └── reports/        # geração PDF (ReportLab)
│   ├── config/             # settings, urls, api (Ninja), auth
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── api/            # clients axios + react-query fetchers
│   │   ├── components/
│   │   │   ├── catalogo/
│   │   │   ├── finance/
│   │   │   ├── finance-dashboard/
│   │   │   ├── produto-editor/
│   │   │   ├── lancamento-editor/
│   │   │   └── reports/
│   │   ├── pages/          # rotas top-level
│   │   ├── types/          # tipos espelhando os schemas do backend
│   │   └── hooks/
│   └── vite.config.ts
├── docs/
│   ├── ARQUITETURA.md      # decisões técnicas, camadas, fluxo de dados
│   └── screenshots/        # capturas usadas no README
└── docker-compose.yml
```

Documentação técnica detalhada: [docs/ARQUITETURA.md](docs/ARQUITETURA.md).

## Decisões de design relevantes

- **Sem libs de gráfico**. Todos os charts (linha, donut, barras horizontais/verticais, sparkline) são SVG cru. Zero dependência de Recharts/Chart.js — controle visual total e bundle menor.
- **Tooltips React custom em vez de `<title>` SVG**. O título HTML nativo é sutil demais (delay de browser); usamos overlays absolutos com hover instantâneo.
- **Mock determinístico no backend, não no frontend**. O endpoint `/api/finance/analytics/*` retorna números fake gerados com `random.seed(42)` baseados em dados reais do catálogo. Trocar pela API real só exige reescrever o service, mantendo o contrato dos schemas.
- **PDFs gerados no servidor com ReportLab**. Layout idêntico em qualquer SO/navegador.
- **AG Grid Community apenas**. Sem licença enterprise — funcionalidades premium foram intencionalmente evitadas.

## Autor

Construído por [Davi Oliveira](https://www.linkedin.com/in/davioliveiraes/).
