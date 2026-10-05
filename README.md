# m3notifybot

Distribuidor de notificaciones vía Telegram con **FastAPI**. Recibe peticiones HTTP de cualquier aplicación o script y las reenvía formateadas directamente a tu chat de Telegram.

```text
Cualquier app / script  ──(POST /notifications)──>  FastAPI  ──>  Telegram Bot  ──>  Tu chat de Telegram
```

---

## 🚀 Inicio rápido (con Docker)

La forma más sencilla de ponerlo en marcha:

```bash
# 1. Clonar el repositorio
git clone <URL_REPOSITORIO>
cd m3notifybot

# 2. Configurar variables de entorno
cp .env.example .env
# Edita .env con tus credenciales (ver siguiente sección)

# 3. Levantar con Docker Compose
docker compose up -d --build
```

El servicio estará disponible en `http://localhost:8500`.

---

## ⚙️ Configuración (`.env`)

Copia `.env.example` a `.env` y rellena las siguientes variables:

| Variable | Descripción | Obligatorio |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Token del bot proporcionado por [@BotFather](https://t.me/BotFather) | Sí |
| `TELEGRAM_CHAT_ID` | Tu ID de chat en Telegram (obtenible vía `@userinfobot` o la API de Telegram) | Sí |
| `NOTIFICATION_API_KEY` | Clave secreta que elijas para autenticar las peticiones entrantes | Sí |
| `DATABASE_URL` | Ruta SQLite (por defecto `sqlite:///data/database.db`) | No |
| `DEBUG` | Activa logs de depuración (`true`/`false`, por defecto `false`) | No |

---

## 📡 Uso de la API

### 1. Comprobar estado del servicio
```bash
curl http://localhost:8500/health
```

### 2. Enviar una notificación
```bash
curl -X POST http://localhost:8500/api/v1/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: tu-clave-api" \
  -d '{
    "source": "mi-servidor",
    "title": "Backup completado",
    "message": "La copia de seguridad se ha realizado con éxito.",
    "severity": "success"
  }'
```

#### Niveles de severidad y formato:
| Severidad | Icono | Uso habitual |
|---|---|---|
| `info` | 🔵 | Mensajes y avisos informativos generales |
| `success` | 🟢 | Tareas completadas o estados correctos |
| `warning` | 🟠 | Advertencias y umbrales de alerta |
| `critical` | 🔴 | Errores graves o caídas de servicios |

> **Documentación interactiva Swagger UI:** Puedes probar la API interactivamente en `http://localhost:8500/docs`.

---

## 💻 Ejecución en local (Desarrollo sin Docker)

Si prefieres ejecutar el proyecto directamente con Python:

```bash
# 1. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate    # En Linux/macOS
.venv\Scripts\activate       # En Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor de desarrollo
uvicorn app.main:app --reload
```

---

## 🛠️ Estructura del Proyecto

```text
m3notifybot/
├── app/
│   ├── api/             # Endpoints /health y /api/v1/notifications
│   ├── core/            # Configuración Pydantic y motor SQLite (WAL)
│   ├── models/          # Modelo de base de datos SQLAlchemy
│   ├── schemas/         # Validación de esquemas Pydantic
│   ├── services/        # Cliente asíncrono para Telegram (httpx)
│   └── utils/           # Formateador visual y escape HTML seguro
├── compose.yml          # Docker Compose para despliegue
├── Dockerfile           # Imagen optimizada con usuario no-root
└── requirements.txt     # Dependencias Python del servicio
```
