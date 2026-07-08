# Arquitetura

Como o **ecommerce-control** está organizado e por quê. Leitura para quem vai estudar ou reaproveitar o código.

> Monólito modular Django + SPA React, conversando por HTTP JSON com bearer token assinado. **Multi-tenant por empresa**: cada conta enxerga apenas os próprios dados.

## 1. Visão geral

```
Browser (React SPA) ──fetch + Bearer token──▶ Django + Ninja (/api/*) ──ORM──▶ PostgreSQL 16
```

3 containers via `docker-compose.yml` (`db`, `backend`, `frontend`), com hot-reload nos dois lados.

## 2. Backend

| App | Responsabilidade |
|---|---|
| `accounts` | `Empresa` (o tenant), CNPJ, onboarding e helpers de tenancy. |
| `catalog` | Categorias, subcategorias, produtos, variações (SKU/EAN). |
| `finance` | Categorias financeiras, lançamentos, visão geral, dashboards. |
| `importer` | Importação de catálogo via planilha (xlsx). |
| `reports` | PDFs com ReportLab — sem modelos próprios. |

Estrutura interna padrão: `models/` (um por arquivo), `routers/` (Ninja), `schemas/` (Pydantic), `services/`, `tests/`, `management/commands/`.

**Por que Django Ninja:** API tipada estilo FastAPI reusando ORM/admin do Django; OpenAPI automático em `/api/docs`; funções em vez de ViewSets.

### Autenticação

Bearer token assinado (`django.core.signing`, TTL default 12h) — sem sessão, sem CSRF. Endpoints em `/api/auth`:

- `register` — cria usuário + empresa (CNPJ validado) e semeia as categorias financeiras; auto-login.
- `login` — usuário **ou** e-mail + senha.
- `esqueci-senha` / `redefinir-senha` — link por e-mail com token de uso único (console em dev, SMTP via env em produção).
- `me`, `empresa` (PUT), `alterar-senha`, `logout`.

### Multi-tenancy

O tenant é a `Empresa` (OneToOne com o usuário — 1 conta = 1 empresa). Todos os modelos de negócio têm FK para `Empresa`; unicidades (nome, slug, SKU) valem **por empresa**.

Regra de ouro (`accounts/tenancy.py`): todo endpoint de dados chama `empresa_do_usuario(request)` e escopa queryset **e** criação por ela. FK simples em vez de schema-por-tenant (`django-tenants`): migrations únicas, zero infra extra.

### Modelos

```
Empresa ─┬─ Categoria ── Subcategoria
         ├─ Produto ── Variação (SKU, margens calculadas em properties)
         ├─ CategoriaFinanceira ── LancamentoFinanceiro
         └─ VisaoGeralPeriodo (funil manual da loja)
```

### Seeds

`seed_catalog --empresa <id|nome> --nicho tech|supermercado [--limpar]` e `seed_finance --empresa ... --meses N`. Determinísticos com `random.seed(42 + empresa.pk)` — reproduzíveis, mas diferentes entre tenants (dados idênticos mascarariam vazamento entre empresas). Nichos novos = uma entrada no dict `NICHOS`.

## 3. Frontend

```
src/
├── api/         # axios + fetchers (1 por recurso)
├── types/       # espelham os schemas Pydantic
├── contexts/    # AuthContext + ThemeContext (únicos estados globais)
├── components/  # por domínio (catalogo/, finance-dashboard/, reports/...)
├── pages/       # 1 por rota
└── hooks/
```

- **Sem Redux** — server state no TanStack Query, UI state em `useState`.
- **Rotas públicas** (`/login`, `/esqueci-senha`, `/redefinir-senha`); o resto atrás de `ProtectedRoute`.
- **Tema claro/escuro** — classe `dark` no `<html>` (Tailwind), persistido em `localStorage`, segue o sistema na primeira visita.
- **Gráficos em SVG cru** (sem Recharts/Chart.js): bundle menor, controle total de paleta nos dois temas, tooltips React instantâneos.
- **AG Grid Community** no catálogo: agrupamento de variações por produto + edição inline de preços com `PATCH`.
- **Formulários** com React Hook Form + Zod (auth usa `useState` direto — poucos campos).

## 4. Relatórios PDF

Cada relatório = router (filtros → `FileResponse`) + service (monta o PDF) + helpers em `pdf_base.py`. Layout padrão: cabeçalho → KPIs → gráficos → tabela. Geração streaming e sempre escopada pela empresa do usuário.

## 5. Convenções

- Imports sem prefixo `apps.` (`from finance.models import ...` — `backend/apps` está no PYTHONPATH).
- Todo router de negócio escopa pela empresa; nunca confiar em ID vindo do cliente.
- Um componente por arquivo, Tailwind direto, comentários só para o *porquê*.

## 6. Testes

```bash
docker compose exec backend python manage.py test
```

Django TestCase com runner customizado (`config/test_runner.py`). Cobre serviços de cálculo, endpoints de catálogo/finance e smoke de PDF. **Lacunas conhecidas:** testes do fluxo de contas, isolamento multi-tenant e suíte de frontend (Vitest).

## 7. Decisões descartadas

| Considerado | Por que descartado |
|---|---|
| DRF | Mais cerimônia que Ninja para a mesma necessidade. |
| Sessões + CSRF | Token assinado é mais simples para SPA stateless. |
| `django-tenants` | FK + escopo no router resolve sem infra extra. |
| Next.js | SSR não ajuda em painel autenticado. |
| Recharts | Bundle grande, tooltip nativo fraco. |
| GraphQL / Celery / Storybook | Complexidade sem demanda no escopo atual. |
