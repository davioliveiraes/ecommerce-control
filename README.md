# Controle Interno - Site Ibeize

## Finalidade

Este projeto tem como finalidade centralizar o controle interno do Site Ibeize, reunindo em uma unica aplicacao a gestao de catalogo, variacoes de produtos, categorias, marcas, lancamentos financeiros, dashboards e relatorios.

A aplicacao foi pensada para apoiar rotinas administrativas do e-commerce, facilitando o cadastro, a consulta, a organizacao dos dados e a visualizacao de informacoes importantes para a operacao.

## Tecnologias Utilizadas

- Python
- Django
- Django Ninja
- PostgreSQL
- React
- TypeScript
- Vite
- Tailwind CSS
- Axios
- React Router
- React Query
- React Hook Form
- Zod
- AG Grid
- Docker
- Docker Compose

## Como Executar

### 1. Pre-requisitos

Antes de iniciar, tenha instalado na maquina:

- Git
- Python 3
- Docker
- Docker Compose

### 2. Clonar o repositorio do GitHub

Clone o projeto:

```powershell
git clone https://github.com/ibeizeloja-oss/ibeize_ecommerce_control.git
```

Entre na pasta do projeto:

```powershell
cd ibeize_ecommerce_control
```

### 3. Criar o ambiente virtual do backend

Entre na pasta do backend:

```powershell
cd backend
```

Crie o ambiente virtual:

```powershell
python -m venv venv
```

Ative o ambiente virtual no Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Atualize o pip:

```powershell
python -m pip install --upgrade pip
```

Instale as dependencias do backend:

```powershell
pip install -r requirements.txt
```

Volte para a raiz do projeto:

```powershell
cd ..
```

Observacao: o ambiente virtual e util para executar comandos Python localmente. Para subir a aplicacao completa, o projeto utiliza Docker.

### 4. Configurar variaveis de ambiente

Crie o arquivo `backend/.env` com as variaveis basicas do Django:

```env
DJANGO_SECRET_KEY=troque-esta-chave-em-desenvolvimento
LANGUAGE_CODE=pt-br
TIME_ZONE=America/Fortaleza
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
AUTH_TOKEN_MAX_AGE_SECONDS=43200
```

O banco PostgreSQL sera configurado automaticamente pelo `docker-compose.yml`.

### 5. Subir o projeto com Docker

Na primeira execucao, crie e construa os containers a partir da raiz do projeto:

```powershell
docker compose up -d --build
```

Depois que os containers ja estiverem criados, inicie os servicos com:

```powershell
docker compose start
```

Servicos disponiveis localmente:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- PostgreSQL: localhost:5432

Para parar os containers sem remove-los:

```powershell
docker compose stop
```

Para recriar as imagens apos mudancas em dependencias ou arquivos Dockerfile:

```powershell
docker compose up -d --build
```

### 6. Acessar a aplicacao

Depois que os containers estiverem rodando, acesse:

- Sistema web: http://localhost:5173
- API do backend: http://localhost:8000/api

## Conceitos Aprendidos

- Estruturacao de uma aplicacao full stack com frontend, backend e banco de dados.
- Criacao de APIs com Django Ninja.
- Modelagem de entidades para catalogo de produtos e controle financeiro.
- Integracao entre React e API usando Axios e React Query.
- Criacao de formularios tipados com React Hook Form e Zod.
- Organizacao de rotas, paginas e componentes reutilizaveis no frontend.
- Uso de grids para listagem e manipulacao de dados administrativos.
- Configuracao de ambiente com Docker e Docker Compose.
- Persistencia de dados com PostgreSQL.
- Separacao de responsabilidades entre apps, schemas, routers, services e componentes.
