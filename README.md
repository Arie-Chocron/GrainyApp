# Grainy app

Aplicacion de ejemplo para practicar desarrollo y despliegue con contenedores:

- **Frontend:** Vue 3, TypeScript, Vite y Tailwind CSS.
- **API:** FastAPI y Uvicorn.
- **Contenedores:** Docker y Docker Compose.
- **Registro de imagenes:** GitHub Container Registry (GHCR).
- **Automatizacion actual:** GitHub Actions construye y publica las imagenes al actualizar `main`.

La pagina muestra un saludo y, al pulsar **Saludar a Grainy**, solicita el mensaje a la API. El proyecto funciona localmente con Docker Compose. Las imagenes estan publicadas en GHCR, pero eso por si solo **no despliega la aplicacion en una pagina publica**.

## Arquitectura

```text
Navegador
   |
   | http://localhost:8080
   v
web (Nginx, puerto 80)
   |
   | /api/* -> api:8000/*
   v
api (FastAPI, puerto 8000)
```

Compose crea una red privada para los servicios. Solo el frontend publica un puerto en el equipo anfitrion: `8080`. La API se alcanza desde Nginx mediante el nombre interno `api`; no se publica directamente en un puerto del anfitrion.

En ejecucion local sin Docker, Vite usa un proxy de desarrollo: envia las solicitudes `/api` a `http://localhost:8000` y elimina el prefijo `/api` antes de llamar a FastAPI.

## Estructura del proyecto

```text
.
|-- api/
|   |-- main.py             # Aplicacion FastAPI y endpoints
|   |-- requirements.txt    # Dependencias Python
|   `-- Dockerfile          # Imagen de la API
|-- web/
|   |-- src/App.vue         # Interfaz y llamada al endpoint de saludo
|   |-- src/assets/         # Recursos graficos
|   |-- package.json        # Scripts y dependencias de Node
|   |-- package-lock.json   # Versiones fijadas para npm ci
|   |-- vite.config.ts      # Vue, Tailwind y proxy para desarrollo
|   |-- nginx.conf          # Sitio estatico y proxy /api en Docker
|   `-- Dockerfile          # Compilacion Vue y servidor Nginx
|-- .github/workflows/
|   |-- ci.yml              # Pruebas, build y Docker en Pull Requests
|   |-- deploy-pages.yml    # Build y despliegue del frontend en Pages
|   `-- publish-images.yml  # Construccion y publicacion de imagenes GHCR
|-- docker-compose.yml      # Servicios, red, healthcheck y puerto local
`-- .gitignore
```

## API

Implementada en `api/main.py`:

| Metodo | Ruta en FastAPI | Respuesta |
|---|---|---|
| `GET` | `/health` | `{"status":"ok"}` |
| `GET` | `/hello` | `{"message":"Hi, i'm Grainy! nice to meet ya!"}` |

Con Docker Compose, Nginx quita el prefijo `/api` y reenvia las rutas. Desde el navegador se usan:

- `http://localhost:8080/api/health`
- `http://localhost:8080/api/hello`

FastAPI tambien ofrece su documentacion interactiva en `/docs`, accesible localmente a traves del proxy como `http://localhost:8080/api/docs`.

## Requisitos para trabajar localmente

- Git.
- Python 3.12 o compatible con las dependencias de `api/requirements.txt`.
- Node.js 22 y npm.
- Docker Desktop con Docker Compose, para ejecutar los contenedores.

### Desarrollo sin Docker

En PowerShell, desde la raiz del repositorio:

```powershell
# API (crear el entorno virtual solo la primera vez)
cd api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Deja la API ejecutandose y abre una segunda terminal:

```powershell
cd web
npm ci
npm run dev
```

Abre la URL local que indique Vite en la terminal. Para compilar y validar Vue/TypeScript:

```powershell
cd web
npm run build
```

### Desarrollo con Docker Compose

Desde la raiz del repositorio:

```powershell
docker compose up --build
```

Abre `http://localhost:8080`. Para detener los servicios, pulsa `Ctrl+C` o usa otra terminal:

```powershell
docker compose down
```

Comandos utiles:

```powershell
docker compose ps
docker compose logs -f
docker compose logs -f api
docker compose logs -f web
```

El servicio `api` tiene un healthcheck que consulta `/health`. Compose espera a que la API este saludable antes de iniciar `web`.

## GitHub y flujos actuales

Repositorio: [Arie-Chocron/GrainyApp](https://github.com/Arie-Chocron/GrainyApp), rama principal `main`.

El workflow [`.github/workflows/publish-images.yml`](.github/workflows/publish-images.yml) se ejecuta:

1. Automaticamente cuando se suben cambios a `main`.
2. Manualmente desde la pestana **Actions**, usando **Run workflow**.

Construye dos imagenes, cada una desde su propio contexto:

| Servicio | Imagen GHCR |
|---|---|
| API | `ghcr.io/arie-chocron/grainy-api` |
| Web | `ghcr.io/arie-chocron/grainy-web` |

Cada ejecucion publica una etiqueta `sha-<commit>` para identificar la version exacta. En la rama principal tambien actualiza `latest`.

El workflow usa el `GITHUB_TOKEN` temporal de GitHub Actions para autenticarse en GHCR. Tiene los permisos minimos declarados en el YAML: lectura del repositorio y escritura de paquetes. No hace falta guardar un token personal en el repositorio.

El workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) se ejecuta al abrir o actualizar un Pull Request hacia `main`. Ejecuta los tests de la API, compila el frontend y construye las dos imagenes sin publicarlas.

El workflow [`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml) compila el frontend con la base `/GrainyApp/`, sube `web/dist` como artefacto y despliega ese artefacto en GitHub Pages al actualizar `main`. Tambien puede ejecutarse manualmente desde Actions.

Para activar Pages en GitHub, selecciona **Settings → Pages → Build and deployment → Source → GitHub Actions**.

El workflow lee la variable de repositorio `VITE_API_URL` (`Settings → Secrets and variables → Actions → Variables`). No es un secreto: la URL de una API publica queda visible en el JavaScript del frontend. Se puede crear cuando la API tenga un host HTTPS.

Mientras `VITE_API_URL` no este definida, el frontend conserva `/api`. Esto permite ejecutar la aplicacion actual por Docker Compose y Vite local; en la pagina publicada de Pages, el boton no podra contactar la API hasta que se configure una URL publica para FastAPI.

Los tres workflows no requieren secretos para estas tareas: usan `GITHUB_TOKEN` y permisos de job limitados. CI valida Pull Requests; el workflow de imagenes publica en GHCR al actualizar `main`; Pages publica el frontend estatico. El despliegue automatico de la API sigue pendiente porque aun no se ha elegido ni configurado su host publico.

## Descargar y ejecutar desde GHCR

Las dos imagenes se publican como paquetes publicos:

- [Paquete `grainy-api`](https://github.com/users/Arie-Chocron/packages/container/package/grainy-api)
- [Paquete `grainy-web`](https://github.com/users/Arie-Chocron/packages/container/package/grainy-web)

Para ejecutarlas en un equipo con Docker:

```powershell
git clone https://github.com/Arie-Chocron/GrainyApp.git
cd GrainyApp
docker compose pull
docker compose up -d
```

Abre `http://localhost:8080`. Para comprobar el estado, consultar logs y detener la aplicacion:

```powershell
docker compose ps
docker compose logs -f
docker compose down
```

`docker compose pull` descarga las imagenes y `docker compose up -d` las inicia en segundo plano. Para reconstruirlas desde el codigo fuente local, usa `docker compose up --build`.

## Estado del despliegue publico

Hasta ahora:

- El codigo esta en GitHub, en `main`.
- GitHub Actions publica las imagenes de API y frontend en GHCR.
- Se comprobo que ambas imagenes se pueden descargar.
- La aplicacion se ha ejecutado y probado localmente en Docker Compose.
- Hay workflows locales preparados para CI en Pull Requests y despliegue del frontend en Pages.

GHCR almacena y distribuye las imagenes; no las ejecuta. La API todavia necesita un host publico con HTTPS. Una posibilidad que se esta evaluando es una VM Linux en un PC propio; esa opcion necesitara configurar disponibilidad y acceso seguro desde internet. No se ha realizado esa configuracion.

GitHub Pages sirve los archivos estaticos de Vue, pero no ejecuta FastAPI. Cuando exista una URL HTTPS publica para la API, se configura como variable `VITE_API_URL`; la API debe permitir el origen `https://arie-chocron.github.io` mediante CORS.
