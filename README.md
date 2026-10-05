# Grainy app

Boilerplate: **Vue 3 + TypeScript + Vite + shadcn-vue** (`web/`) y **FastAPI** (`api/`).

## Docker
Desde la carpeta raíz del proyecto:

    docker compose up --build

Compose construye el frontend y la API; el frontend espera a que el healthcheck de la API pase antes de iniciar. Abre http://localhost:8080. Nginx sirve el frontend y reenvía `/api` a la API; por ejemplo:

- http://localhost:8080/api/health
- http://localhost:8080/api/hello

Para detener los contenedores, usa `Ctrl+C` y después `docker compose down`.

## Publicar y desplegar imágenes GHCR

GitHub Actions construye y publica `ghcr.io/arie-chocron/grainy-api` y `ghcr.io/arie-chocron/grainy-web` al hacer push a `main`. Cada imagen recibe una etiqueta con el commit y la etiqueta `latest`.

La primera publicación de cada paquete puede quedar privada por defecto. Para hacerla pública, abre el paquete en GitHub, entra en **Package settings** y selecciona **Change visibility** → **Public**. Repite el proceso para ambas imágenes.

En un servidor con Docker Compose, descarga las últimas imágenes y arranca la aplicación desde la raíz del proyecto:

    docker compose pull
    docker compose up -d

Para ver el estado y los logs:

    docker compose ps
    docker compose logs -f

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
