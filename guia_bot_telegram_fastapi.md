# Guía: Bot de Telegram como distribuidor de notificaciones con FastAPI

## 1. Objetivo

Construir un pequeño servicio que actúe como **distribuidor de notificaciones**:

```text
Aplicación A ─┐
Aplicación B ─┼─> FastAPI ─> Bot de Telegram ─> Tu usuario de Telegram
Aplicación C ─┘
```

Las aplicaciones externas harán peticiones HTTP a FastAPI. FastAPI validará la notificación y el bot enviará el mensaje a tu chat de Telegram.

### Características de la primera versión

- Un único destinatario de Telegram.
- Endpoint HTTP `POST /notifications`.
- Autenticación sencilla mediante API key.
- Bot de Telegram creado con BotFather.
- Configuración mediante variables de entorno.
- Docker opcional.
- Arquitectura preparada para añadir posteriormente más destinatarios, persistencia, reintentos o colas.

---

## 2. Arquitectura recomendada

La versión inicial puede ser deliberadamente sencilla:

```text
                    ┌─────────────────────┐
                    │  Aplicaciones       │
                    │  externas           │
                    └──────────┬──────────┘
                               │
                         POST /notifications
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │                     │
                    │  - autenticar       │
                    │  - validar payload  │
                    │  - formatear        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Telegram Bot API    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Tu chat de Telegram │
                    └─────────────────────┘
```

### Separación de responsabilidades

Conviene mantener separadas estas piezas:

- `api.py`: endpoints HTTP.
- `telegram.py`: comunicación con Telegram.
- `models.py`: modelos Pydantic.
- `config.py`: configuración.
- `main.py`: arranque de FastAPI.

No es necesario introducir una base de datos ni una cola en la primera versión.

---

## 3. Crear el bot de Telegram

En Telegram abre **@BotFather**.

Ejecuta:

```text
/newbot
```

BotFather te pedirá:

1. Nombre del bot.
2. Username del bot.

Al terminar obtendrás un token parecido a:

```text
123456789:AAExampleToken...
```

**No publiques este token ni lo subas a Git.**

Guárdalo como variable de entorno:

```env
TELEGRAM_BOT_TOKEN=...
```

---

## 4. Obtener tu `chat_id`

El bot necesita saber a qué conversación enviar las notificaciones.

Primero abre el bot que acabas de crear y pulsa **Start**.

Después puedes consultar:

```text
https://api.telegram.org/bot<TU_TOKEN>/getUpdates
```

La respuesta contendrá una estructura JSON similar a:

```json
{
  "result": [
    {
      "message": {
        "chat": {
          "id": 123456789,
          "type": "private"
        }
      }
    }
  ]
}
```

El valor:

```text
123456789
```

es tu `TELEGRAM_CHAT_ID`.

No confundas el `chat_id` con el token del bot.

---

## 5. Crear el proyecto

Una estructura razonable:

```text
telegram-notifier/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api.py
│   ├── config.py
│   ├── models.py
│   └── telegram.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Crear el entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Linux/macOS:

```bash
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

---

## 6. Dependencias

`requirements.txt`:

```text
fastapi
uvicorn[standard]
httpx
pydantic-settings
```

Instalación:

```bash
pip install -r requirements.txt
```

### ¿Por qué `httpx`?

El servicio puede llamar directamente a la API HTTP de Telegram.

Para este caso sencillo no necesitamos obligatoriamente una librería específica de Telegram. Esto reduce dependencias y hace muy explícita la integración.

---

## 7. Configuración

`app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_chat_id: int
    notification_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
```

`.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:TU_TOKEN
TELEGRAM_CHAT_ID=123456789
NOTIFICATION_API_KEY=cambia-esta-clave
```

`.env.example`:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
NOTIFICATION_API_KEY=
```

### Importante

Añade `.env` a `.gitignore`:

```text
.env
.venv/
__pycache__/
*.pyc
```

---

## 8. Modelo de una notificación

Queremos aceptar un payload sencillo pero suficientemente genérico.

`app/models.py`:

```python
from pydantic import BaseModel, Field


class Notification(BaseModel):
    source: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=4000)
    severity: str = Field(default="info", max_length=20)
```

Ejemplo:

```json
{
  "source": "monitoring",
  "title": "Servidor caído",
  "message": "El servidor web no responde.",
  "severity": "critical"
}
```

Podemos ampliar posteriormente el modelo con:

```text
timestamp
url
environment
application
metadata
```

---

## 9. Cliente de Telegram

`app/telegram.py`:

```python
import httpx

from .config import settings
from .models import Notification


class TelegramError(Exception):
    pass


async def send_notification(notification: Notification) -> None:
    url = (
        f"https://api.telegram.org/"
        f"bot{settings.telegram_bot_token}/sendMessage"
    )

    text = (
        f"🔔 <b>{notification.title}</b>\n\n"
        f"<b>Origen:</b> {notification.source}\n"
        f"<b>Nivel:</b> {notification.severity}\n\n"
        f"{notification.message}"
    )

    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, json=payload)

    if response.is_error:
        raise TelegramError(
            f"Telegram API error: {response.status_code} "
            f"{response.text}"
        )
```

La función es asíncrona porque FastAPI trabaja muy bien con I/O asíncrono y no necesitamos bloquear un worker mientras esperamos la respuesta de Telegram.

---

## 10. Endpoint de FastAPI

`app/api.py`:

```python
from fastapi import APIRouter, Header, HTTPException, status

from .config import settings
from .models import Notification
from .telegram import TelegramError, send_notification


router = APIRouter()


@router.post("/notifications", status_code=status.HTTP_202_ACCEPTED)
async def create_notification(
    notification: Notification,
    x_api_key: str = Header(...),
):
    if x_api_key != settings.notification_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    try:
        await send_notification(notification)
    except TelegramError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to deliver notification to Telegram",
        )

    return {
        "status": "accepted",
    }
```

---

## 11. Aplicación principal

`app/main.py`:

```python
from fastapi import FastAPI

from .api import router


app = FastAPI(
    title="Telegram Notification Dispatcher",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

Arrancar:

```bash
uvicorn app.main:app --reload
```

La API estará disponible en:

```text
http://127.0.0.1:8000
```

Y la documentación interactiva de FastAPI:

```text
http://127.0.0.1:8000/docs
```

---

## 12. Probar el servicio

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Enviar una notificación:

```bash
curl -X POST \
  http://127.0.0.1:8000/notifications \
  -H "Content-Type: application/json" \
  -H "X-API-Key: cambia-esta-clave" \
  -d '{
    "source": "mi-aplicacion",
    "title": "Nuevo evento",
    "message": "Se ha creado un nuevo registro.",
    "severity": "info"
  }'
```

Si todo está correctamente configurado, recibirás el mensaje en Telegram.

---

## 13. Diseño del contrato HTTP

Una aplicación externa solamente necesita conocer:

```text
POST /notifications
X-API-Key: <clave>
Content-Type: application/json
```

Body:

```json
{
  "source": "string",
  "title": "string",
  "message": "string",
  "severity": "info"
}
```

Esto permite que prácticamente cualquier aplicación pueda integrarse:

```text
Python
Java
Node.js
JavaScript
PHP
Go
.NET
n8n
GitHub Actions
Jenkins
Prometheus/Alertmanager
scripts Bash
etc.
```

---

## 14. Mejorar el formato de Telegram

Una notificación podría quedar visualmente así:

```text
🔴 Servidor caído

Origen: monitoring
Nivel: critical

El servidor web no responde.
```

Una función de formateo dedicada permite cambiar la presentación sin modificar el endpoint:

```python
def format_notification(notification: Notification) -> str:
    icons = {
        "info": "🔵",
        "warning": "🟠",
        "critical": "🔴",
        "success": "🟢",
    }

    icon = icons.get(notification.severity, "🔔")

    return (
        f"{icon} <b>{notification.title}</b>\n\n"
        f"<b>Origen:</b> {notification.source}\n"
        f"<b>Nivel:</b> {notification.severity}\n\n"
        f"{notification.message}"
    )
```

Esto es preferible a mezclar la lógica de presentación con la lógica HTTP.

---

## 15. Seguridad mínima

Para un servicio que recibe peticiones de Internet, no conviene exponer un endpoint completamente abierto.

### Mínimo recomendable

1. API key.
2. HTTPS.
3. Token de Telegram exclusivamente en variables de entorno.
4. No almacenar tokens en Git.
5. Validación mediante Pydantic.
6. Límites de tamaño del mensaje.
7. Logs sin secretos.
8. Rate limiting si el endpoint queda expuesto públicamente.

### API key

La primera versión puede utilizar:

```text
X-API-Key
```

Más adelante puedes sustituirlo por:

- JWT.
- HMAC.
- OAuth2.
- claves independientes por aplicación.
- allowlist de IPs.

---

## 16. Una mejora importante: no esperar a Telegram

La implementación anterior hace:

```text
HTTP request
     │
     ▼
FastAPI
     │
     ▼
Telegram
     │
     ▼
respuesta HTTP
```

Esto significa que la aplicación que envía la notificación tiene que esperar a que Telegram responda.

Para un sistema pequeño es perfectamente válido.

Sin embargo, si quieres convertirlo en un auténtico **notification dispatcher**, es mejor desacoplar ambos pasos:

```text
Aplicación
    │
    ▼
FastAPI
    │
    ▼
Cola
    │
    ▼
Worker
    │
    ▼
Telegram
```

Por ejemplo:

```text
Redis + worker
```

o:

```text
RabbitMQ + worker
```

o incluso una cola basada en una base de datos.

Entonces FastAPI puede responder rápidamente:

```http
202 Accepted
```

y el worker se ocupa de entregar el mensaje.

---

## 17. Reintentos

Telegram puede no estar disponible temporalmente.

Por eso, en una arquitectura más robusta:

```text
Notificación
     │
     ▼
Cola
     │
     ▼
Worker
     │
     ├── éxito ─────> FIN
     │
     └── error
           │
           ▼
        retry
           │
           ├── retry 1
           ├── retry 2
           └── retry 3
```

Recomendación:

- 3-5 reintentos.
- Backoff exponencial.
- Registrar el error.
- Después de varios fallos, enviar a una dead-letter queue.

---

## 18. Evitar duplicados

Una aplicación podría enviar accidentalmente dos veces la misma notificación.

Para sistemas más serios conviene introducir un identificador:

```json
{
  "id": "evt_01JXYZ...",
  "source": "billing",
  "title": "Pago recibido",
  "message": "Pago recibido correctamente.",
  "severity": "success"
}
```

La aplicación podría generar el `id`.

El dispatcher puede almacenar los IDs procesados y rechazar duplicados.

Esto se conoce como **idempotencia**.

---

## 19. Evolución recomendada del proyecto

### V1 — MVP

```text
FastAPI
   ↓
Telegram
```

Características:

- Un destinatario.
- API key.
- Sin base de datos.
- Sin cola.

Es la versión que se recomienda implementar primero.

### V2 — Producción pequeña

```text
FastAPI
   ↓
Redis
   ↓
Worker
   ↓
Telegram
```

Añadir:

- reintentos;
- logs estructurados;
- rate limiting;
- idempotencia;
- Docker.

### V3 — Dispatcher completo

```text
                    ┌─> Telegram
                    │
Aplicaciones -> API -> Cola -> Worker
                    │
                    ├─> Email
                    │
                    ├─> Discord
                    │
                    └─> Slack
```

Aquí el concepto deja de ser simplemente "un bot de Telegram" y se convierte en un **notification gateway**.

---

## 20. Docker

Un `Dockerfile` sencillo:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construir:

```bash
docker build -t telegram-notifier .
```

Ejecutar:

```bash
docker run --rm \
  -p 8000:8000 \
  --env-file .env \
  telegram-notifier
```

---

## 21. Despliegue

Para un proyecto pequeño puedes desplegar el contenedor en:

- un VPS;
- una máquina propia;
- una instancia cloud;
- Kubernetes si ya existe infraestructura Kubernetes.

La configuración típica sería:

```text
Internet
   │
   ▼
HTTPS / reverse proxy
   │
   ▼
FastAPI
   │
   ▼
Telegram API
```

Si lo expones a Internet, utiliza HTTPS y evita publicar directamente un servidor de desarrollo.

Para producción:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

y preferiblemente colócalo detrás de un reverse proxy como Nginx, Caddy o un balanceador cloud.

---

## 22. Logs

Los logs deberían servir para diagnosticar problemas sin revelar secretos.

Ejemplo:

```text
2026-08-24 08:30:10 INFO notification_received source=monitoring severity=critical
2026-08-24 08:30:10 INFO telegram_delivery_success
```

No registrar:

```text
TELEGRAM_BOT_TOKEN=...
X-API-Key=...
```

Si utilizas logging estructurado, será mucho más sencillo buscar:

```text
source=monitoring
severity=critical
notification_id=evt_123
```

---

## 23. Tests

Como mínimo probaría:

### `GET /health`

Debe devolver:

```json
{
  "status": "ok"
}
```

### API key incorrecta

Debe devolver:

```http
401 Unauthorized
```

### Payload inválido

Debe devolver:

```http
422 Unprocessable Entity
```

### Telegram correcto

Debe devolver:

```http
202 Accepted
```

### Telegram caído

Debe devolver:

```http
502 Bad Gateway
```

Para los tests de Telegram no conviene llamar a Telegram realmente. Es mejor mockear `httpx`.

---

## 24. Recomendación final de implementación

No empezaría con Redis, RabbitMQ, PostgreSQL, Docker Compose y Kubernetes.

Para este caso concreto, empezaría con:

```text
FastAPI
   │
   ├── Pydantic
   │
   ├── API key
   │
   └── httpx
          │
          ▼
     Telegram Bot API
```

Cuando el MVP funcione, añadiría en este orden:

```text
1. Logging
2. Tests
3. Docker
4. Rate limiting
5. Cola + worker
6. Reintentos
7. Idempotencia
8. Múltiples destinatarios
9. Persistencia
10. Panel/configuración
```

La decisión arquitectónica importante es **mantener el contrato `/notifications` estable**. Así, las aplicaciones que generan notificaciones no tienen que cambiar cuando internamente sustituyas:

```text
FastAPI → Telegram
```

por:

```text
FastAPI → Redis → Worker → Telegram
```

o posteriormente:

```text
FastAPI → Notification Service → Telegram/Slack/Email/Discord
```

---

## 25. Resultado esperado

Al terminar el MVP tendrás un endpoint como:

```http
POST https://tu-dominio.com/notifications
```

que cualquier aplicación autorizada podrá utilizar:

```json
{
  "source": "mi-app",
  "title": "Backup completado",
  "message": "El backup de producción ha terminado correctamente.",
  "severity": "success"
}
```

y tú recibirás automáticamente en Telegram:

```text
🟢 Backup completado

Origen: mi-app
Nivel: success

El backup de producción ha terminado correctamente.
```

Ese diseño es pequeño, fácil de mantener y proporciona una base limpia para evolucionar hacia un verdadero servicio centralizado de notificaciones.
