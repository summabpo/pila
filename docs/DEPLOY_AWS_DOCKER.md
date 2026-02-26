# Despliegue del microservicio PILA en AWS con Docker

Guía para subir el microservicio PILA a AWS usando contenedores Docker.

---

## 1. Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) instalado
- Cuenta en [Docker Hub](https://hub.docker.com/) (para el flujo recomendado)
- Servidor AWS EC2 con Docker (o similar)

---

## 2. Flujo recomendado: Docker Hub + EC2

Este flujo es el más sencillo y funciona igual desde Mac (ARM) y Ubuntu (amd64).

### 2.1 Build local (con plataforma linux/amd64)

El flag `--platform linux/amd64` garantiza que la imagen funcione en servidores x86 (Ubuntu en EC2) aunque construyas desde Mac con chip M1/M2:

```bash
cd pila
docker build --platform linux/amd64 -t sat1124/pila:1 .
```

Incrementa el tag en cada release (ej: `:1`, `:2`, `:1.1`).

### 2.2 Push a Docker Hub

```bash
docker push sat1124/pila:1
```

(Requiere `docker login` previo si no lo has hecho.)

### 2.3 En el servidor AWS (Ubuntu)

```bash
docker pull sat1124/pila:1
docker run -d \
  --name pila \
  --restart always \
  -p 8001:8001 \
  --env-file .env \
  sat1124/pila:1
```

El archivo `.env` en el servidor debe tener `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE`, `PILA_SERVICE_TOKEN`.

### 2.4 Actualizar versión en el servidor

```bash
docker stop pila && docker rm pila
docker pull sat1124/pila:2   # nueva versión
docker run -d --name pila --restart always -p 8001:8001 --env-file .env sat1124/pila:2
```

---

## 3. Probar localmente

```bash
docker run --rm -p 8001:8001 \
  -e DB_NAME=pila \
  -e DB_USER=usuario \
  -e DB_PASSWORD=secret \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e PILA_SERVICE_TOKEN=tu-token \
  sat1124/pila:1
```

En macOS/Windows, `host.docker.internal` apunta al host. En Linux usa la IP del host o la red del host.

---

## 4. Alternativa: Amazon ECR

Si prefieres mantener las imágenes dentro de AWS (compliance, costos):

### 4.1 Crear repositorio ECR

```bash
aws ecr create-repository --repository-name pila --region us-east-1
```

Anota el URI que devuelve (ej: `123456789012.dkr.ecr.us-east-1.amazonaws.com/pila`).

### 4.2 Autenticación Docker con ECR

```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
```

Reemplaza `123456789012` por tu Account ID y `us-east-1` por tu región.

### 4.3 Etiquetar y subir imagen

```bash
docker build --platform linux/amd64 -t 123456789012.dkr.ecr.us-east-1.amazonaws.com/pila:1 .
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/pila:1
```

---

## 5. Otras opciones de despliegue en AWS

### Opción A: ECS Fargate

1. Crear cluster ECS.
2. Definir Task Definition que use la imagen de ECR.
3. Crear servicio ECS con la task definition.
4. Configurar ALB (Application Load Balancer) para exponer el puerto 8001.

Variables de entorno en la Task Definition:

| Variable | Descripción |
|----------|-------------|
| `DB_NAME` | Nombre de la base PostgreSQL |
| `DB_USER` | Usuario de la base |
| `DB_PASSWORD` | Contraseña (usar Secrets Manager) |
| `DB_HOST` | Host de RDS o instancia PostgreSQL |
| `DB_PORT` | 5432 |
| `DB_SSLMODE` | `require` (recomendado en RDS) |
| `PILA_SERVICE_TOKEN` | Token Bearer para autenticación API |

### Opción B: AWS App Runner

1. Crear servicio App Runner desde imagen ECR.
2. Configurar variables de entorno en la consola o con IaC.
3. App Runner gestiona el balanceador y el escalado.

### Opción C: EC2 + Docker Compose

1. Lanzar EC2 con Docker instalado.
2. Clonar el repo o copiar la imagen desde Docker Hub/ECR.
3. Ejecutar con `docker run` o `docker-compose`.

---

## 6. Despliegue en servidor con Nginx Proxy Manager

Si pila corre en el mismo servidor que Nomiweb y usas NPM:

### 6.1 docker-compose para pila

Crea `docker-compose.yml` en el servidor (o junto al de Nomiweb):

```yaml
services:
  pila:
    image: sat1124/pila:1
    env_file:
      - .env
    environment:
      DJANGO_SETTINGS_MODULE: pila_service.settings
    expose:
      - "8001"
    ports:
      - "8001:8001"
    restart: always
    networks:
      - proxy-network

networks:
  proxy-network:
    external:
      name: nginx-proxy_proxy
```

### 6.2 Archivo .env en el servidor

```env
DB_NAME=pila
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
DB_SSLMODE=require
PILA_SERVICE_TOKEN=
```

### 6.3 Proxy Host en Nginx Proxy Manager

- **Domain:** `pila.tudominio.com`
- **Forward Hostname:** `pila` (nombre del servicio) o IP del contenedor
- **Forward Port:** `8001`
- **Scheme:** `http`

---

## 7. Configuración de producción (settings)

Para producción, conviene:

1. **DEBUG = False** (variable de entorno `DEBUG=0`)
2. **SECRET_KEY** desde variable de entorno
3. **ALLOWED_HOSTS** con el dominio/host de la API

Puedes crear `pila_service/settings_production.py` que importe de `settings` y sobrescriba estos valores, o usar variables de entorno si las soporta tu configuración actual.

---

## 8. Integración con Nomiweb

En Nomiweb, configura la URL del microservicio PILA (ej. en variables de entorno o settings):

```
PILA_SERVICE_URL=https://pila.tudominio.com
```

El cliente `pila_cliente` en Nomiweb debe usar esta URL para las peticiones POST a `/api/v1/pila/planillas/`.

---

## 9. Comandos útiles

```bash
# Build (desde Mac o Ubuntu)
docker build --platform linux/amd64 -t sat1124/pila:1 .

# Push
docker push sat1124/pila:1

# Logs del contenedor
docker logs -f pila

# Entrar al contenedor
docker exec -it pila sh

# Verificar salud (local)
curl -H "Authorization: Bearer $PILA_SERVICE_TOKEN" http://localhost:8001/api/v1/pila/planillas/
```

---

## 10. Sugerencias adicionales

| Sugerencia | Descripción |
|------------|-------------|
| **Versionado** | Usa tags semánticos (`:1`, `:1.1`, `:2`) para poder hacer rollback si algo falla. |
| **docker-compose** | Si usas compose, `docker-compose pull && docker-compose up -d` actualiza sin parar otros servicios. |
| **Backup .env** | Guarda una copia segura del `.env` del servidor; sin él no podrás levantar el contenedor. |
| **Logs** | `docker logs -f pila` para depurar; considera redirigir a un archivo si necesitas historial. |
| **Healthcheck** | Opcional: añadir `HEALTHCHECK` en el Dockerfile para que Docker/Orquestadores detecten si la app cae. |
