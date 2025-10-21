# Face Microservice (Original Estável)
Versão simples: **sem ângulos**, retorna **score** em `/verify`, demo `/demo` com **Cadastrar** e **Verificar**.

## Rodar (Docker)
```
docker compose up -d --build
```
- Swagger: http://localhost:8000/docs
- Demo: http://localhost:8000/demo

## Endpoints
- `POST /enroll` → `name`, `image`
- `POST /verify` → `image`, `action?` ⇒ `{ matched, user, score }`
- `GET /events` → logs (SQLite)
