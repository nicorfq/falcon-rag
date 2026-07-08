# Sistema de Rastreo RutaSur — Documentación Técnica Interna

**Versión:** 2.1.0  
**Equipo responsable:** Datos y Sistemas  
**Última actualización:** enero 2026  
**Confidencialidad:** Uso interno

---

## Descripción general

El sistema de rastreo de RutaSur permite el seguimiento en tiempo real de todos los envíos activos en la red. Está compuesto por tres capas:

1. **Capa de ingesta** — recibe eventos de los dispositivos móviles de los repartidores y de los centros de distribución
2. **Capa de procesamiento** — normaliza, valida y persiste los eventos en la base de datos
3. **Capa de exposición** — la API REST (`api.rutasur.cl/v2`) que consumen el sitio web, la app móvil y las integraciones con tiendas asociadas

---

## Formato del número de seguimiento

Todos los números de seguimiento siguen el formato:

```
RS + 10 dígitos numéricos
```

**Ejemplo:** `RS0043921785`

El número se genera automáticamente cuando el paquete es admitido en la red (estado `ADMITIDO`). Es único e irrepetible. Los repartidores lo escanean mediante código de barras o QR impreso en la etiqueta del paquete.

---

## Estados del sistema

| Código | Descripción | Acción siguiente |
|--------|-------------|-----------------|
| `ADMITIDO` | Paquete ingresado a la red | Sistema inicia conteo de plazo |
| `EN_TRANSITO` | En movimiento entre centros | Ninguna acción requerida |
| `EN_REPARTO` | Salió a entrega hoy | Notificación automática al cliente |
| `ENTREGADO` | Entregado al destinatario | Cierre del caso |
| `INTENTO_FALLIDO` | Intento sin éxito | Sistema agenda reintento |
| `EN_SUCURSAL` | En sucursal para retiro | Notificación al cliente con dirección y plazo |
| `DEVUELTO` | Devuelto al remitente | Notificación al remitente |

---

## Frecuencia de actualización

El rastreo se actualiza cada **4 horas**. Los eventos de los repartidores se envían en tiempo real desde la app móvil, pero el sistema consolida y expone el estado visible al cliente en ciclos de 4 horas para garantizar consistencia.

---

## Configuración del entorno de desarrollo

### Requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (caché de estados)
- Docker y Docker Compose

### Variables de entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/rutasur_tracking
REDIS_URL=redis://localhost:6379/0

# API
API_SECRET_KEY=<generada con openssl rand -hex 32>
API_TOKEN_EXPIRY_HOURS=24

# Notificaciones
SMTP_HOST=smtp.rutasur.cl
SMTP_PORT=587
SMTP_USER=noreply@rutasur.cl
```

### Levantar entorno local

```bash
git clone https://github.com/rutasur-internal/tracking-api.git
cd tracking-api
cp .env.example .env        # Completar variables
docker compose up -d        # Levanta DB + Redis
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## Endpoints principales

Ver documentación completa en `API_Rastreo_RutaSur.json`.

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/v2/envios/{numero_seguimiento}` | Estado actual del envío |
| `GET` | `/v2/envios/{numero_seguimiento}/eventos` | Historial completo de eventos |
| `GET` | `/v2/estados` | Catálogo de estados válidos |

---

## Umbrales de alerta operacional

El sistema de monitoreo dispara alertas automáticas en los siguientes casos:

- Envío sin movimiento por más de **3 días hábiles** → alerta nivel medio (notificación a soporte)
- Envío sin movimiento por más de **15 días hábiles** → alerta nivel crítico (inicio de proceso de extravío)
- Más de **3 intentos fallidos** → estado cambia automáticamente a `EN_SUCURSAL`

---

## Contacto del equipo

Para consultas técnicas o incidencias del sistema:  
📧 `sistemas@rutasur.cl`  
📞 Interno 2201 (horario hábil)

