# Integração com a API da Nuvemshop

Este guia mostra como substituir o **mock determinístico** das abas "Visão geral" e "Produtos" do Dashboard Finance por dados reais da API oficial da Nuvemshop.

A boa notícia: o mock e a API real foram desenhados para compartilharem o **mesmo contrato** (schemas em `backend/apps/finance/routers/analytics.py`). Você só precisa reescrever o serviço — o frontend não muda.

> Documentação oficial: <https://tiendanube.github.io/api-documentation/intro>

---

## 1. Cadastro da aplicação

A Nuvemshop usa **OAuth 2 (authorization code)** para autorizar apps de parceiros.

1. Crie sua conta de parceiro em <https://partners.nuvemshop.com.br>.
2. Cadastre uma "App" no painel. Você recebe:
   - `client_id`
   - `client_secret`
   - `redirect_uri` (deve bater com o configurado)
3. Defina os **scopes** necessários:
   - `read_products` — catálogo (abas Produtos)
   - `read_orders` — pedidos (Visão geral, ranking de vendidos)
   - `read_customers` — opcional, se for popular dados de cliente

## 2. Fluxo OAuth

```
[Lojista]                      [Sua app]                    [Nuvemshop]
    │                              │                              │
    │ clica "Conectar Nuvemshop"   │                              │
    ├─────────────────────────────►│                              │
    │                              │ redireciona p/ autorização   │
    │                              ├─────────────────────────────►│
    │                              │                              │
    │ ◄────── tela de consentimento ──────────────────────────────│
    │                                                             │
    │ autoriza ─────────────────────────────────────────────────► │
    │                              │  callback: ?code=...&store_id│
    │                              │ ◄────────────────────────────│
    │                              │                              │
    │                              │ POST /apps/authorize/token   │
    │                              ├─────────────────────────────►│
    │                              │ { access_token, store_id }   │
    │                              │ ◄────────────────────────────│
    │                              │                              │
    │                              │ persistir token + store_id   │
```

**Endpoint de troca de código por token**:

```http
POST https://www.nuvemshop.com.br/apps/authorize/token
Content-Type: application/x-www-form-urlencoded

client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
&grant_type=authorization_code
&code={CODE_RECEBIDO_NO_CALLBACK}
```

**Resposta**:

```json
{
  "access_token": "abc123...",
  "token_type": "bearer",
  "scope": "read_products,read_orders",
  "user_id": 12345
}
```

O `user_id` é o **store_id** que vai entrar na URL base de toda chamada subsequente.

## 3. Modelo de persistência sugerido

Crie um modelo Django para guardar a credencial por loja:

```python
# backend/apps/integrations/models.py
class LojaNuvemshop(models.Model):
    store_id = models.BigIntegerField(unique=True)
    access_token = models.CharField(max_length=255)
    scopes = models.CharField(max_length=255)
    conectada_em = models.DateTimeField(auto_now_add=True)
    desconectada_em = models.DateTimeField(null=True, blank=True)
```

Tokens da Nuvemshop **não expiram** por padrão — não é necessário refresh flow. O lojista pode desconectar manualmente, então trate `401 Unauthorized` como sinal de revogação.

## 4. Chamadas autenticadas

### Base URL versionada

```
https://api.nuvemshop.com.br/2025-03/{store_id}
```

> A versão atual da API é **2025-03**. Mudanças breaking bumpam o marcador — fixar a versão evita quebras silenciosas.

### Headers obrigatórios

| Header | Valor | Observação |
|---|---|---|
| `Authentication` | `bearer {access_token}` | Note a grafia: é `Authentication`, **não** `Authorization` |
| `User-Agent` | `MinhaApp (contato@dominio.com)` | Sem isso, retorna **400 Bad Request** |
| `Content-Type` | `application/json; charset=utf-8` | Apenas para POST/PUT |

### Exemplo em Python (requests)

```python
import requests

BASE_URL = "https://api.nuvemshop.com.br/2025-03"
USER_AGENT = "Ecommerce Internal Suite (davioliveiraes@gmail.com)"

def nuvemshop_get(store_id: int, token: str, path: str, params: dict | None = None):
    response = requests.get(
        f"{BASE_URL}/{store_id}{path}",
        headers={
            "Authentication": f"bearer {token}",
            "User-Agent": USER_AGENT,
        },
        params=params or {},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()
```

## 5. Rate limit

| Plano | Bucket | Taxa |
|---|---|---|
| Básico | 40 req | 2 req/s |
| Next / Evolution | 400 req | 20 req/s |

Cada resposta traz headers úteis:

- `x-rate-limit-limit` — tamanho do bucket
- `x-rate-limit-remaining` — quanto resta
- `x-rate-limit-reset` — ms até o bucket esvaziar

Estratégia recomendada: **wrapper que detecta `429`** e respeita o `x-rate-limit-reset` com `time.sleep`.

## 6. Paginação

Todos os endpoints de listagem aceitam `page` e `per_page` (máx. **200** itens por página). Headers de navegação:

- `x-total-count` — total absoluto
- `Link` — URLs `rel="next"` / `rel="prev"` / `rel="first"` / `rel="last"`

Padrão: parse do `Link` e iteração até `rel="next"` sumir.

## 7. Mapeamento mock → API real

Cada bloco abaixo mostra o trecho do mock e o que substituir por chamada à API.

### 7.1 KPI cards (Visitas / Vendas / Receita / Ticket médio)

**Hoje** (`build_overview()` em `analytics_service.py`):

```python
visitas_total = rng.randint(2800, 5200)
taxa_conversao = rng.uniform(0.018, 0.035)
vendas_total = int(round(visitas_total * taxa_conversao))
```

**Real**:

```python
pedidos = paginate(
    nuvemshop_get,
    path="/orders",
    params={
        "payment_status": "paid",
        "created_at_min": data_inicio.isoformat(),
        "created_at_max": data_fim.isoformat(),
        "per_page": 200,
        "fields": "id,total,created_at",
    },
)
vendas_total = len(pedidos)
receita_total = sum(Decimal(p["total"]) for p in pedidos)
ticket_medio = receita_total / vendas_total if vendas_total else Decimal("0")
```

**Visitas não tem endpoint nativo.** A API Nuvemshop não expõe contadores de tráfego. Opções:

- **GA4** — `google-analytics-data` (Python SDK), query `runReport` sobre `sessions` e `screenPageViews`.
- **Plausible** — endpoint `GET /api/v1/stats/timeseries`.
- **Pixel próprio** — instrumentar a loja via Script Tag (`/scripts`) e enviar para seu backend.

### 7.2 Comportamento do visitante (funil)

| Item do mock | Origem real |
|---|---|
| Total de visitas | GA4 `sessions` |
| Visualização de categoria | GA4 `screenPageViews` filtrado por `page_path` da categoria |
| Visualização de produto | Mesmo, filtrado por `/produtos/*` |
| Carrinhos criados | `GET /orders?status=open` (todos não-fechados) |

### 7.3 Comportamento de checkout

A API expõe checkouts abandonados via `payment_status=abandoned`:

```http
GET /2025-03/{store_id}/orders?payment_status=abandoned&created_at_min=...
```

Combine com os contagens por `payment_status` para montar o funil:

- `abandoned` → checkout iniciado mas não pago
- `pending` → criado, aguardando confirmação
- `paid` → finalizado

### 7.4 Rankings de produto

```python
# Pedidos pagos no período → linhas de produto
pedidos_pagos = paginate(
    nuvemshop_get,
    path="/orders",
    params={
        "payment_status": "paid",
        "created_at_min": data_inicio.isoformat(),
        "per_page": 200,
        "fields": "id,products,total",
    },
)

# Agregar vendas por variant_id
from collections import defaultdict
vendas_por_variant = defaultdict(lambda: {"qtd": 0, "receita": Decimal("0")})

for pedido in pedidos_pagos:
    for linha in pedido["products"]:
        v = vendas_por_variant[linha["variant_id"]]
        v["qtd"] += linha["quantity"]
        v["receita"] += Decimal(linha["price"]) * linha["quantity"]
```

Depois, busque os metadados dos produtos:

```http
GET /2025-03/{store_id}/products?ids=10,15,22,...&per_page=200
```

> ⚠️ O parâmetro `ids` aceita **até 30 IDs por chamada** — pagine se o ranking for maior.

### 7.5 Estoque crítico

```http
GET /2025-03/{store_id}/products?per_page=200
```

Cada produto retorna `variants[]` com `stock` (inteiro ou `null` para "ilimitado"). Filtre `stock <= 3 and stock is not None`.

## 8. Webhooks (recomendado)

Em vez de polling, registre webhooks para receber eventos em tempo real:

```http
POST /2025-03/{store_id}/webhooks
{
  "event": "order/paid",
  "url": "https://meudominio.com/webhooks/nuvemshop/order-paid"
}
```

Eventos úteis para o dashboard:

- `order/created`, `order/paid`, `order/cancelled`
- `product/created`, `product/updated`
- `app/uninstalled` — derruba a conexão localmente

A Nuvemshop assina o payload com HMAC SHA-256 usando o `client_secret` — sempre valide.

## 9. Errors esperados

| Status | Significado | Ação |
|---|---|---|
| `400` | JSON inválido **ou** falta `User-Agent` | Conferir headers e body |
| `401` | Token revogado ou inválido | Marcar loja como `desconectada` e pedir reauth |
| `402` | Loja suspensa por falta de pagamento | Notificar o lojista |
| `404` | Recurso não existe | Tratar como vazio |
| `422` | Validação semântica | Logar o payload e o `details` da resposta |
| `429` | Rate limit | Respeitar `x-rate-limit-reset` |
| `5xx` | Erro do servidor | Retry exponencial (3 tentativas) |

## 10. Roadmap de implementação sugerido

1. **App `integrations/`** com modelo `LojaNuvemshop` + endpoints `/oauth/start` e `/oauth/callback`.
2. **Cliente HTTP** (`integrations/nuvemshop_client.py`) com paginação, rate limit e retry.
3. **Substituição incremental do mock**:
   - 3a. `build_products()` → catálogo + variants real.
   - 3b. KPIs de vendas/receita/ticket → pedidos reais.
   - 3c. Funil de checkout → orders com `payment_status` agrupado.
4. **Telemetria externa** (GA4 ou Plausible) para visitas/views.
5. **Webhooks** para invalidar cache do TanStack Query no frontend.
6. **Multi-loja**: middleware que injeta `store_id` na request com base no usuário autenticado.

---

## Referências rápidas

- Visão geral da API: <https://tiendanube.github.io/api-documentation/intro>
- Recurso Product: <https://tiendanube.github.io/api-documentation/resources/product>
- Recurso Order: <https://tiendanube.github.io/api-documentation/resources/order>
- Webhooks: <https://tiendanube.github.io/api-documentation/resources/webhook>
- Partners (cadastro de app): <https://partners.nuvemshop.com.br>
