# Grainy app

Boilerplate: **Vue 3 + TypeScript + Vite + shadcn-vue** (`web/`) y **FastAPI** (`api/`).

## Docker
Desde la carpeta raíz del proyecto:

    docker compose up --build

Compose construye el frontend y la API; el frontend espera a que el healthcheck de la API pase antes de iniciar. Abre http://localhost:8080. Nginx sirve el frontend y reenvía `/api` a la API; por ejemplo:

- http://localhost:8080/api/health
- http://localhost:8080/api/hello

Para detener los contenedores, usa `Ctrl+C` y después `docker compose down`.

## Desarrollo local
    # API
    cd api && python -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt && uvicorn main:app --reload
    # Web (proxy /api -> localhost:8000)
    cd web && npm install && npm run dev

## Agregar componentes shadcn
    cd web && npx shadcn-vue@latest add dialog
(`components.json` ya está configurado.)

## Endpoints
- `GET /api/hello` -> `{"message": "Hi, i'm Grainy! nice to meet ya!"}`
- `GET /api/health` -> `{"status": "ok"}`
