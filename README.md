# Grainy app

Aplicacion de ejemplo para practicar desarrollo y despliegue con contenedores:

- **Frontend:** Vue 3, TypeScript, Vite y Tailwind CSS.
- **API:** FastAPI y Uvicorn.
- **Contenedores:** Docker y Docker Compose.
- **Registro de imagenes:** GitHub Container Registry (GHCR).
- **Automatizacion:** GitHub Actions valida Pull Requests, publica imagenes y despliega el frontend en Pages.

La pagina publica esta en [GitHub Pages](https://arie-chocron.github.io/GrainyApp/). Al pulsar **Saludar a Grainy**, solicita el mensaje a la API. El frontend ya esta publicado; la API publica se prepara aparte usando una VM Linux propia y un Cloudflare Quick Tunnel temporal.

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
|   |-- deploy-api.yml      # Despliegue de API en runner de la VM
|   |-- deploy-pages.yml    # Build y despliegue del frontend en Pages
|   `-- publish-images.yml  # Construccion y publicacion de imagenes GHCR
|-- docker-compose.prod.yml # API con tag de imagen y Cloudflare Quick Tunnel
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

GitHub Pages esta configurado para usar **Settings → Pages → Build and deployment → Source → GitHub Actions**. El frontend publicado esta en [https://arie-chocron.github.io/GrainyApp/](https://arie-chocron.github.io/GrainyApp/).

El workflow lee la variable de repositorio `VITE_API_URL` (`Settings → Secrets and variables → Actions → Variables`). No es un secreto: la URL de una API publica queda visible en el JavaScript del frontend. Se puede crear cuando la API tenga un host HTTPS.

Mientras `VITE_API_URL` no este definida, el frontend conserva `/api`. Esto mantiene Docker Compose y Vite local funcionando. En Pages, el boton no podra contactar la API hasta crear la variable con la URL publica de FastAPI y volver a ejecutar el workflow de Pages.

El workflow [`.github/workflows/deploy-api.yml`](.github/workflows/deploy-api.yml) espera a que `Publish Docker images` termine correctamente en `main` y ejecuta el despliegue en el runner `grainy-deploy` de la VM. Usa la misma etiqueta inmutable `sha-<commit>` que publico GHCR; no despliega `latest`.

El workflow de despliegue no necesita secretos de GitHub: GHCR es publico y el runner ya esta en la VM. El registro del runner usa un token temporal generado por GitHub, que se introduce directamente en la VM y nunca se guarda en el repositorio.

CI corre en runners alojados por GitHub y nunca en la VM. Solo el despliegue de la API usa el runner propio; su trigger y filtro limitan el job a la finalizacion exitosa del workflow de imagenes para la rama `main`. Un runner propio puede acceder al Docker del host y debe tratarse como una maquina privilegiada; no se deben ejecutar alli workflows de Pull Requests ni codigo de forks.

## API en VM con Cloudflare Quick Tunnel (prueba temporal)

La configuracion de [docker-compose.prod.yml](docker-compose.prod.yml) ejecuta la imagen de la API con un tag `IMAGE_TAG` obligatorio y la conecta a Cloudflare Quick Tunnel. La API no publica un puerto del host; cloudflared es el unico camino entrante y crea una URL HTTPS aleatoria `trycloudflare.com`.

Quick Tunnel no requiere cuenta ni dominio, pero Cloudflare lo recomienda solo para pruebas: no tiene garantia de disponibilidad, el hostname cambia cada vez que se crea el tunel y cualquiera que conozca la URL puede acceder. Al apagar o reiniciar el contenedor cloudflared, la URL puede cambiar. Por eso, despues de un cambio de URL hay que actualizar `VITE_API_URL` y volver a desplegar Pages. Para uso permanente se necesitara un hostname estable y un tunel nombrado.

### Preparar el host

1. Crea una VM Linux x64 (por ejemplo Ubuntu Server LTS), mantenla encendida y habilita su conectividad saliente a GitHub, GHCR y Cloudflare. Como el runner y el tunel inician conexiones salientes, no se necesita abrir puertos en el router ni asignar una IP publica a la VM.
2. Instala Docker Engine y el plugin Docker Compose siguiendo la [guia oficial para Ubuntu](https://docs.docker.com/engine/install/ubuntu/). Comprueba la instalacion con `docker --version` y `docker compose version`.
3. Crea un usuario separado para el despliegue e inicia una sesion nueva con el:

   ```bash
   sudo adduser --disabled-password --gecos "" deploy
   sudo usermod -aG docker deploy
   su - deploy
   ```

   Ser miembro del grupo `docker` equivale, en la practica, a tener privilegios de root. Usa una VM dedicada y no ejecutes workflows de Pull Requests en este runner.
4. En GitHub ve a **Settings → Actions → Runners → New self-hosted runner**, elige **Linux x64** y sigue los comandos que muestra la pagina para descargar y configurar el runner bajo el usuario `deploy`. Puedes dejar vacias las etiquetas adicionales: el workflow selecciona el runner con las etiquetas predeterminadas `self-hosted`, `linux` y `x64`. El token de registro expira y solo se usa durante este registro; no lo copies en archivos del repositorio.
5. Desde el directorio del runner, instalalo e inicialo como servicio. Verifica que Docker esta disponible para ese usuario:

   ```bash
   sudo ./svc.sh install
   sudo ./svc.sh start
   sudo ./svc.sh status
   docker ps
   ```

   La [documentacion oficial](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners) describe el registro y la [configuracion del runner como servicio](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/configure-the-application).
6. Confirma que el runner aparece **Idle** en **Settings → Actions → Runners**. El servicio `cloudflared` no requiere instalar otro programa en el host: `docker-compose.prod.yml` lo ejecuta como contenedor con `restart: unless-stopped`.
7. Revisa **Settings → Environments → production**. En la fase de aprobacion se configuraran sus revisores antes de habilitar el despliegue protegido.

GitHub recomienda usar runners propios solo con repositorios privados: una PR de un fork puede intentar ejecutar codigo peligroso en el equipo del runner. Este repositorio es publico, asi que mantener el runner para esta prueba es una decision con riesgo, aunque el CI de PR use `ubuntu-latest` y el runner de VM solo reciba el workflow de despliegue desde `main`. Usa una VM dedicada, no guardes secretos adicionales en ella, revisa y aprueba personalmente cada cambio antes de integrarlo y nunca cambies el job de CI para que use `grainy-deploy`. Consulta la [advertencia oficial de GitHub](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/add-runners#adding-a-self-hosted-runner-to-a-repository).

### Runner propio frente a despliegue por SSH

Se recomienda el runner propio para esta prueba: se conecta hacia GitHub, por lo que no hay que abrir SSH ni redirigir puertos entrantes en el router, y puede ejecutar Docker Compose directamente en la VM. SSH desde un runner hospedado por GitHub requeriria hacer accesible el SSH de la VM desde Internet y administrar una clave privada y reglas de red. El coste de la simplicidad del runner propio es que la VM debe estar encendida y protegida; pertenecer al grupo `docker` otorga privilegios muy amplios.

### Primer despliegue de API

Con el runner **Idle**, integra el cambio en `main`. El push ejecutara `Publish Docker images` y, cuando termine correctamente, `Deploy API to home VM` ejecutara `docker compose pull` y `docker compose up -d` con el tag exacto `sha-<commit>`. Si necesitas repetir la publicacion, puedes abrir **Actions → Publish Docker images → Run workflow** y elegir `main`.

En los logs del job `Deploy API image to VM`, busca `Temporary API URL: https://...trycloudflare.com`. Tambien puedes ver el URL y los logs del tunel en la VM con:

```bash
docker compose --project-name grainy-prod --file docker-compose.prod.yml logs -f cloudflared
```

Configura entonces la variable de repositorio `VITE_API_URL` con esa URL HTTPS sin barra final, por ejemplo `https://example.trycloudflare.com`. En **Actions → Deploy frontend to GitHub Pages → Run workflow**, elige `main` para compilar Pages con el nuevo endpoint. La API ya permite el origen de Pages mediante CORS.

No integres el cambio que activa `deploy-api.yml` en `main` hasta que el runner de la VM aparezca **Idle** en **Settings → Actions → Runners**.

Para comprobar la API manualmente, sustituye el hostname por el que genero el tunel:

```text
https://<hostname-actual>.trycloudflare.com/health
https://<hostname-actual>.trycloudflare.com/hello
```

Si la VM o cloudflared se reinician y el hostname cambia, actualiza la variable `VITE_API_URL` y vuelve a desplegar Pages. No almacenes ese URL en el codigo: es configuracion de despliegue.

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
- La CI de Pull Requests paso: tests de API, build web y builds de ambas imagenes.
- GitHub Pages publica el frontend en `https://arie-chocron.github.io/GrainyApp/`.
- El workflow de despliegue de API y Compose para la VM estan preparados; falta registrar y mantener activo el runner en una VM Linux.

GHCR almacena y distribuye las imagenes; no las ejecuta. La VM del PC todavia debe prepararse y registrarse para ejecutar la API. Cloudflare Quick Tunnel es solo para la prueba inicial; el enlace es temporal y el PC debe permanecer encendido.

GitHub Pages sirve los archivos estaticos de Vue, pero no ejecuta FastAPI. Hasta que se despliegue la API y se configure `VITE_API_URL`, el sitio esta visible pero el boton de saludo no puede completar la llamada.
