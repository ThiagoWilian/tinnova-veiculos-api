# Tinnova Veículos API

API REST para gerenciamento de veículos com FastAPI, PostgreSQL, Redis e autenticação JWT via OAuth2.

## Estrutura do Projeto

```text
app/
  api/
    dependencies.py        # autenticação e autorização por papel
    v1/
      endpoints/          # rotas HTTP (auth, veiculos)
      router.py           # agregador das rotas da API
  core/                   # config, database, redis, security, errors
  models/                 # modelos SQLAlchemy (Veiculo, User)
  repositories/           # acesso a dados e queries
  schemas/                # contratos Pydantic de entrada e saída
  services/               # regras de negócio (auth, cotacao, veiculo)
  main.py                 # criação da aplicação FastAPI
scripts/
  init_db.py              # cria tabelas, usuários e veículos de exemplo
tests/
  api/                    # testes de controllers/endpoints
  e2e/                    # fluxo integrado principal
  repositories/           # testes da camada de dados
  unit/                   # testes de services
```

A aplicação é inicializada em `app/main.py`, registra os handlers de erro, configura CORS e inclui as rotas de `app/api/v1/router.py`.

## Variáveis de Ambiente

Crie um arquivo `.env` a partir de `.env.example` antes de subir a aplicação:

```bash
cp .env.example .env
```

Variáveis disponíveis:

- `DATABASE_URL`: string de conexão do banco PostgreSQL.
- `REDIS_URL`: URL de conexão com o Redis.
- `JWT_SECRET_KEY`: chave usada para assinar os tokens JWT.
- `JWT_ALGORITHM`: algoritmo de assinatura JWT, por padrão `HS256`.
- `JWT_EXPIRE_MINUTES`: tempo de expiração do token em minutos.
- `COTACAO_TTL_SECONDS`: TTL do cache Redis para a cotação USD/BRL.
- `ADMIN_EMAIL` e `ADMIN_PASSWORD`: credenciais do usuário administrador inicial.
- `USER_EMAIL` e `USER_PASSWORD`: credenciais do usuário comum inicial.

## Como Rodar Localmente

Suba PostgreSQL, Redis e API com Docker Compose:

```bash
docker compose up -d
```

Inicialize tabelas, usuários e veículos de exemplo:

```bash
docker compose exec api python -m scripts.init_db
```

A API ficará disponível em:

- Swagger: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

## Rodando Sem Docker Para a API

Para rodar sem Docker, instale e inicie PostgreSQL e Redis localmente, ou aponte `DATABASE_URL` e `REDIS_URL` no `.env` para instâncias já disponíveis. Depois, execute a API localmente:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m scripts.init_db
uvicorn app.main:app --reload
```

## Dados Iniciais

O `scripts/init_db.py` cria:

- ADMIN: email definido por `ADMIN_EMAIL` e senha por `ADMIN_PASSWORD` no `.env`.
- USER: email definido por `USER_EMAIL` e senha por `USER_PASSWORD` no `.env`.
- Veículos de exemplo das marcas Toyota, Volkswagen, Chevrolet e Ford.

Valores padrão no `.env.example`:

- ADMIN: `admin@tinnova.com` / `admin123`
- USER: `user@tinnova.com` / `user123`

## Endpoints

### Autenticação

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=admin@tinnova.com&password=admin123
```

Use o `access_token` retornado no header das chamadas protegidas:

```http
Authorization: Bearer <token>
```

### Veículos

- `GET /veiculos`
- `GET /veiculos?marca=Toyota&ano=2022&cor=Prata`
- `GET /veiculos?minPreco=10000&maxPreco=30000`
- `GET /veiculos/{id}`
- `POST /veiculos` (ADMIN)
- `PUT /veiculos/{id}` (ADMIN)
- `PATCH /veiculos/{id}` (ADMIN)
- `DELETE /veiculos/{id}` (ADMIN)
- `GET /veiculos/relatorios/por-marca`

Parâmetros aceitos em `GET /veiculos`:

- `marca`: filtra por marca, ignorando diferença entre maiúsculas e minúsculas.
- `ano`: filtra por ano.
- `cor`: filtra por cor, ignorando diferença entre maiúsculas e minúsculas.
- `minPreco`: preço mínimo em USD armazenado.
- `maxPreco`: preço máximo em USD armazenado.
- `page`: página atual, padrão `1`.
- `size`: quantidade de itens por página, padrão `20` e máximo `100`.
- `sort_by`: campo de ordenação (`marca`, `modelo`, `ano`, `cor`, `preco_usd`, `created_at`).
- `sort_dir`: direção da ordenação (`asc` ou `desc`), padrão `desc`.

Exemplo de cadastro:

```json
{
  "marca": "Toyota",
  "modelo": "Corolla",
  "ano": 2022,
  "cor": "Prata",
  "placa": "ABC1D23",
  "preco_brl": "100000.00"
}
```

A API recebe `preco_brl`, consulta a cotação USD/BRL e persiste o valor convertido em `preco_usd`.

Exemplo de resposta paginada:

```json
{
  "items": [
    {
      "id": "3df6423b-d7be-427b-9016-f0e536c13f41",
      "marca": "Toyota",
      "modelo": "Corolla",
      "ano": 2022,
      "cor": "Prata",
      "placa": "ABC1D23",
      "preco_usd": "20000.00",
      "ativo": true
    }
  ],
  "page": 1,
  "size": 20,
  "total": 1
}
```

Exemplo de resposta do relatório por marca:

```json
[
  {
    "marca": "Toyota",
    "quantidade": 3
  },
  {
    "marca": "Volkswagen",
    "quantidade": 3
  }
]
```

## Padrão de Erros

Os erros seguem o formato:

```json
{
  "detail": {
    "code": "VEHICLE_PLATE_CONFLICT",
    "message": "Placa ja cadastrada"
  }
}
```

Códigos usados pela aplicação:

- `UNAUTHORIZED`: HTTP 401 para token ausente, inválido ou usuário inativo.
- `FORBIDDEN`: HTTP 403 para usuário sem permissão administrativa.
- `NOT_FOUND`: HTTP 404 para recurso não encontrado.
- `VEHICLE_PLATE_CONFLICT`: HTTP 409 para placa já cadastrada.
- `VALIDATION_ERROR`: HTTP 422 para payload ou parâmetros inválidos.
- `CURRENCY_RATE_UNAVAILABLE`: HTTP 503 quando não é possível obter a cotação USD/BRL.

## Testes

Instale as dependências e rode:

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q --cov=app --cov-fail-under=75
```

Organização dos testes:

- `tests/unit/`: services, incluindo duplicidade de placa, filtros e validações de PUT/PATCH.
- `tests/repositories/`: filtros e constraint de placa única na camada de dados.
- `tests/api/`: controllers/endpoints, incluindo cenários 401, 403, 409 e payload de erro padronizado.
- `tests/e2e/`: fluxo integrado de obter token, criar veículo como ADMIN, listar/filtrar e detalhar.

Os testes usam SQLite em memória e mockam a cotação para evitar chamadas externas.