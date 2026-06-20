# Warden

Agente autónomo de detección y remediación de degradación de servicios para Plataformas Internas de Desarrollo (Internal Developer Platforms).

Warden recibe señales de degradación de servicios mediante webhooks, analiza la situación utilizando un LLM y ejecuta una acción de remediación de forma autónoma o la escala a un humano cuando es necesario.

## Requisitos

- Docker y Docker Compose
- API Key de Groq (https://console.groq.com)

## Configuración

1. Clonar el repositorio:
   ```bash
    git clone <repo-url>
    cd warden
    ````

2. Crear el archivo de entorno:

   ```bash
   cp .env.example .env
   ```

   Configura tu `GROQ_API_KEY` en el archivo `.env`.

3. Iniciar los servicios:

   ```bash
   docker compose up --build
   ```

   El servicio estará disponible en `http://localhost:9000`.

4. Ejecutar las pruebas:

   ```bash
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   PYTHONPATH=. pytest tests/ -v
   ```

## API

| Método | Ruta                   | Descripción                                       |
| ------ | ---------------------- | ------------------------------------------------- |
| GET    | /health                | Verificación del estado del servicio              |
| GET    | /events                | Listar eventos recibidos                          |
| GET    | /events/:id            | Detalle de un evento junto con la decisión tomada |
| GET    | /approvals             | Solicitudes de aprobación pendientes              |
| POST   | /approvals/:id/approve | Aprobar y ejecutar una acción                     |
| POST   | /approvals/:id/reject  | Rechazar una acción pendiente                     |

## Decisiones de arquitectura

* **FastAPI** — Framework HTTP asíncrono, ideal para la recepción de webhooks.
* **PostgreSQL** — Almacenamiento persistente para eventos, decisiones y solicitudes de aprobación.
* **SQLAlchemy + Alembic** — ORM y gestión de migraciones.
* **Groq (llama-3.3-70b-versatile)** — LLM utilizado para el razonamiento; dispone de un nivel gratuito.
* **Los handlers están simulados (mocked)** — No se invoca ningún orquestador ni sistema de mensajería real.

## Suposiciones

* El campo `context` es opcional y extensible.
* El único entorno considerado como producción es `prod`.
* El límite de historial es configurable mediante la variable de entorno `HISTORY_LIMIT` (valor predeterminado: `5`).

### Restricciones de `safe_to_auto`

| Condición                                          | Efecto                         |
| -------------------------------------------------- | ------------------------------ |
| `severity == critical`                             | `safe_to_auto = false` siempre |
| `confidence < 0.7`                                 | `safe_to_auto = false`         |
| `env == prod` y `action` en `rollback`, `scale_up` | `safe_to_auto = false`         |

