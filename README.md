# Extrator de Faturas Monorepo

Monorepo com:

- `apps/api`: backend em FastAPI (multi-tenant, RBAC, JWT, Alembic, seed, pytest)
- `apps/web`: frontend em Next.js + TypeScript
- `packages/shared`: tipos/contratos compartilhados
- `infra`: recursos de infraestrutura local

## Subir local (1 comando)

```bash
docker compose up --build
```

Serviços:

- Web: http://localhost:3000
- API: http://localhost:8000
- Health: http://localhost:8000/health
- MinIO API: http://localhost:9000
- MinIO Console: http://localhost:9001

## Seed inicial

O container da API executa automaticamente:

1. `alembic upgrade head`
2. `python -m app.seed`

Usuário seed:

- email: `admin@demo.com`
- senha: `admin123`
- role: `admin`

## Ambientes

- `apps/api/.env.example`
- `apps/web/.env.example`

## Qualidade de código

### Backend (`apps/api`)

- Lint: `ruff check .`
- Format: `black .`
- Testes: `pytest`

### Frontend (`apps/web`)

- Lint: `npm run lint`
- Format: `npm run format`
