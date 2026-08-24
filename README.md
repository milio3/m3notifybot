# m3notifybot

Distribuidor de notificaciones via Telegram. Recibe mensajes HTTP de cualquier aplicación y los envía como notificaciones a tu chat de Telegram.

```text
Aplicación A ─┐
Aplicación B ─┼─> FastAPI ─> Bot de Telegram ─> Tu chat de Telegram
Aplicación C ─┘
```

---

## Arquitectura

```text
m3notifybot/
├── app/
│   ├── main.py              # Instancia FastAPI y ciclo de vida
│   ├── core/
│   │   ├── config.py        # Configuración con Pydantic Settings
│   │   └── database.py      # Motor SQLite con modo WAL
│   ├── api/
│   │   ├── health.py        # GET /health y GET /ready
│   │   └── v1/
│   │       └── notifications.py  # POST /api/v1/notifications
│   ├── schemas/
│   │   └── notification.py  # Esquemas Pydantic (entrada/salida)
│   ├── models/
│   │   └── notification.py  # Modelo ORM (SQLAlchemy)
│   ├── services/
│   │   └── telegram.py      # Cliente Telegram (httpx)
│   └── utils/
│       └── formatter.py     # Formateador visual de notificaciones
├── tests/                   # Tests con pytest
├── data/                    # Base de datos SQLite (no versionado)
├── compose.yml              # Docker Compose para despliegue
├── Dockerfile               # Imagen Docker con usuario no-root
└── requirements.txt         # Dependencias Python
```

---

## Variables de entorno

| Variable | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | `str` | Sí | Token del bot obtenido de BotFather |
| `TELEGRAM_CHAT_ID` | `int` | Sí | ID del chat destinatario |
| `NOTIFICATION_API_KEY` | `str` | Sí | Clave para autenticar peticiones |
| `DATABASE_URL` | `str` | No | Ruta SQLite (por defecto `sqlite:///data/database.db`) |
| `HTTP_TIMEOUT_SECONDS` | `float` | No | Timeout HTTP en segundos (por defecto `10.0`) |
| `DEBUG` | `bool` | No | Modo depuración (por defecto `false`) |

---

## Instalación local (desarrollo)

### 1. Clonar y crear entorno virtual

```bash
git clone <URL_REPOSITORIO> m3notifybot
cd m3notifybot
python -m venv .venv
```

### 2. Activar el entorno

En Windows:

```powershell
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tu token de Telegram, chat_id y clave API
```

### 5. Arrancar el servicio

```bash
uvicorn app.main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000` y la documentación interactiva en `http://127.0.0.1:8000/docs`.

---

## Uso

### Health check

```bash
curl http://127.0.0.1:8000/health
```

### Enviar una notificación

```bash
curl -X POST \
  http://127.0.0.1:8000/api/v1/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-clave-api" \
  -d '{
    "source": "mi-aplicacion",
    "title": "Nuevo evento",
    "message": "Se ha creado un nuevo registro.",
    "severity": "info"
  }'
```

### Niveles de severidad

| Severidad | Icono |
|---|---|
| `info` | 🔵 |
| `warning` | 🟠 |
| `critical` | 🔴 |
| `success` | 🟢 |

---

## Tests

```bash
pytest tests/ -v
```

---

## Despliegue con Docker

### Construir y arrancar

```bash
docker compose up -d --build
```

El servicio estará disponible en el **puerto 8500**.

### Verificar

```bash
curl http://localhost:8500/health
```

---

## Primer despliegue en el servidor (Raspberry Pi)

```bash
# 1. Crear directorios
sudo mkdir -p /opt/apps/m3notifybot /mnt/dietpi_userdata/apps/m3notifybot/data /mnt/dietpi_userdata/backups/m3notifybot
sudo chown -R dev:dev /opt/apps/m3notifybot /mnt/dietpi_userdata/apps/m3notifybot /mnt/dietpi_userdata/backups/m3notifybot

# 2. Clonar repositorio
cd /opt/apps
git clone <URL_REPOSITORIO> m3notifybot
cd m3notifybot

# 3. Configurar entorno
cp .env.example .env
nano .env

# 4. Construir y arrancar
docker compose up -d --build
```

---

## Actualización en producción

```bash
ssh dev@127.0.0.1
cd /opt/apps/m3notifybot
git fetch --tags
git checkout v<NUEVA_VERSION>
docker compose up -d --build
```

---

## Rollback

```bash
ssh dev@127.0.0.1
cd /opt/apps/m3notifybot
git checkout v<VERSION_ANTERIOR>
docker compose up -d --build
curl -f http://localhost:8500/health
```

---

## Backup de la base de datos

> **Importante:** En modo WAL, nunca copiar directamente el fichero `.db` con `cp` mientras la app esté activa.

Comando de respaldo en caliente:

```bash
sqlite3 /mnt/dietpi_userdata/apps/m3notifybot/data/database.db ".backup '/mnt/dietpi_userdata/backups/m3notifybot/db_$(date +%Y%m%d_%H%M%S).db'"
```

---

## Registro de puertos

| Aplicación | Puerto del host |
|---|---|
| m3notifybot | `8500` |
