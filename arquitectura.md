# Arquitectura del Sistema de Notificaciones Automáticas
## GreenH Project - OpenSolar Integration

**Fecha:** 04 de octubre de 2025  
**Versión:** 1.0

---

## 1. Visión General del Sistema

El sistema de notificaciones automáticas tiene como objetivo mantener informados a los clientes sobre el progreso de sus proyectos solares mediante emails profesionales y estéticos. Las notificaciones se activan automáticamente cuando se completan acciones específicas en OpenSolar, comenzando desde el momento en que se marca el pago de la cuota inicial.

### Objetivos principales:
1. Notificar automáticamente a clientes cuando cambie el estado de acciones en sus proyectos
2. Iniciar notificaciones a partir del pago de cuota inicial
3. Enviar emails profesionales con diseño limpio y estético
4. Incluir credenciales de acceso al portal de clientes en el primer mensaje
5. Proporcionar descripciones claras de cada actualización del proyecto

---

## 2. Arquitectura del Sistema

### 2.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                          OpenSolar                              │
│                    (Sistema de Gestión)                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Webhook POST
                     │ (cuando cambia project.actions)
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend Flask (Webhook Receiver)                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. Recibir webhook de OpenSolar                         │  │
│  │  2. Validar y parsear datos del proyecto                 │  │
│  │  3. Identificar acción completada                        │  │
│  │  4. Verificar si debe notificar                          │  │
│  │  5. Generar contenido del email                          │  │
│  │  6. Enviar email vía Gmail API                           │  │
│  │  7. Registrar notificación en base de datos              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Gmail API
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Gmail (admin@greenhproject.com)               │
│                      Envío de Emails                            │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Email
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente Final                           │
│                    (Recibe notificaciones)                      │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Datos

#### Estructura del Webhook de OpenSolar:
```json
{
  "timestamp": "2025-10-04T19:00:00Z",
  "model": "project",
  "action": "update",
  "data": {
    "project": {
      "id": 7772938,
      "identifier": "GHP-2024-001",
      "title": "Proyecto Solar - Cliente X",
      "address": "Dirección del proyecto",
      "contacts_data": [
        {
          "email": "cliente@example.com",
          "first_name": "Juan",
          "family_name": "Pérez",
          "phone": "+57 300 1234567"
        }
      ],
      "actions": [
        {
          "id": 1226451,
          "title": "Pago de cuota inicial",
          "events": [
            {
              "id": 40061178,
              "is_complete": true,
              "completion_date": "2025-10-04T19:00:00Z",
              "who": {
                "display": "Carlos Acosta",
                "email": "carlos@greenhproject.com"
              }
            }
          ]
        }
      ]
    }
  }
}
```

---

## 3. Componentes Detallados

### 3.1 Backend Flask (Webhook Receiver)

**Tecnología:** Python 3.11 + Flask  
**Despliegue:** Render o Railway (plan gratuito)  
**Base de datos:** SQLite (para registro de notificaciones)

#### Endpoints:

##### 1. `POST /webhook/opensolar`
- **Propósito:** Recibir webhooks de OpenSolar
- **Autenticación:** Token personalizado en headers
- **Procesamiento:**
  1. Validar origen del webhook
  2. Parsear datos del proyecto
  3. Identificar acciones completadas recientemente
  4. Verificar si es la primera notificación (pago cuota inicial)
  5. Generar y enviar email
  6. Registrar en base de datos

##### 2. `GET /health`
- **Propósito:** Health check para el servicio
- **Respuesta:** `{"status": "ok", "timestamp": "..."}`

##### 3. `GET /notifications/<project_id>`
- **Propósito:** Consultar historial de notificaciones de un proyecto
- **Autenticación:** API Key
- **Respuesta:** Lista de notificaciones enviadas

#### Estructura de la Base de Datos:

```sql
-- Tabla de notificaciones enviadas
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    project_identifier TEXT,
    action_id INTEGER NOT NULL,
    action_title TEXT NOT NULL,
    recipient_email TEXT NOT NULL,
    recipient_name TEXT,
    email_type TEXT NOT NULL, -- 'first_notification' o 'progress_update'
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_subject TEXT,
    email_body TEXT,
    status TEXT DEFAULT 'sent', -- 'sent', 'failed', 'pending'
    error_message TEXT,
    webhook_data TEXT -- JSON completo del webhook
);

-- Tabla de configuración
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_project_id ON notifications(project_id);
CREATE INDEX idx_sent_at ON notifications(sent_at);
CREATE INDEX idx_status ON notifications(status);
```

#### Lógica de Procesamiento:

```python
def process_webhook(webhook_data):
    """
    Procesar webhook de OpenSolar y enviar notificaciones
    """
    project = webhook_data['data']['project']
    project_id = project['id']
    
    # 1. Obtener acciones completadas recientemente
    completed_actions = get_recently_completed_actions(project['actions'])
    
    if not completed_actions:
        return {"status": "no_actions_to_notify"}
    
    # 2. Verificar si es la primera notificación
    is_first_notification = check_if_first_notification(project_id)
    
    # 3. Obtener datos del cliente
    client_data = project['contacts_data'][0]  # Primer contacto
    
    # 4. Para cada acción completada
    for action in completed_actions:
        # Verificar si ya notificamos esta acción
        if already_notified(project_id, action['id']):
            continue
        
        # Generar email
        if is_first_notification and is_initial_payment_action(action):
            email_content = generate_first_notification_email(
                client_data, project, action
            )
            is_first_notification = False  # Marcar como enviada
        else:
            email_content = generate_progress_update_email(
                client_data, project, action
            )
        
        # Enviar email
        send_email_via_gmail(
            to=client_data['email'],
            subject=email_content['subject'],
            html_body=email_content['html'],
            plain_body=email_content['plain']
        )
        
        # Registrar notificación
        save_notification(project_id, action, client_data, email_content)
    
    return {"status": "success", "notifications_sent": len(completed_actions)}
```

### 3.2 Sistema de Templates de Email

**Tecnología:** Jinja2 para templates HTML

#### Template 1: Primera Notificación (Pago de Cuota Inicial)

**Asunto:** "¡Bienvenido a GreenH Project! - Acceso a tu Portal de Cliente"

**Contenido:**
- Saludo personalizado
- Confirmación del pago de cuota inicial
- **Credenciales de acceso al portal:**
  - URL: https://www.greenhproject.com/gestionproyectos
  - ID del proyecto: [project_identifier]
  - Instrucciones de acceso
- Descripción del siguiente paso
- Información de contacto
- Diseño limpio con colores corporativos

#### Template 2: Actualización de Progreso

**Asunto:** "Actualización de tu Proyecto Solar - [Acción Completada]"

**Contenido:**
- Saludo personalizado
- Descripción de la acción completada
- Contexto y explicación del avance
- Próximos pasos
- Enlace al portal para más detalles
- Información de contacto

#### Diseño de Templates:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        /* Estilos basados en la paleta de GreenH Project */
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 20px auto;
            background: #ffffff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .content {
            padding: 30px;
        }
        .action-box {
            background: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .credentials-box {
            background: #FFF3E0;
            border: 2px solid #FF9800;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
        }
        .button {
            display: inline-block;
            padding: 12px 30px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 0;
        }
        .footer {
            background: #f9f9f9;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <!-- Template content here -->
</body>
</html>
```

### 3.3 Integración con Gmail API

**Cuenta de envío:** admin@greenhproject.com  
**Método:** Gmail API (OAuth 2.0)

#### Configuración:
1. Crear proyecto en Google Cloud Console
2. Habilitar Gmail API
3. Configurar OAuth 2.0 credentials
4. Obtener refresh token para la cuenta admin@greenhproject.com
5. Almacenar credenciales de forma segura (variables de entorno)

#### Código de envío:
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

def send_email_via_gmail(to, subject, html_body, plain_body):
    """
    Enviar email usando Gmail API
    """
    creds = Credentials(
        token=None,
        refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('GMAIL_CLIENT_ID'),
        client_secret=os.getenv('GMAIL_CLIENT_SECRET')
    )
    
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = 'admin@greenhproject.com'
    message['subject'] = subject
    
    part1 = MIMEText(plain_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    
    message.attach(part1)
    message.attach(part2)
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    result = service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()
    
    return result
```

---

## 4. Configuración de Webhook en OpenSolar

### 4.1 Parámetros del Webhook

```json
{
  "endpoint": "https://notificaciones-greenhproject.onrender.com/webhook/opensolar",
  "headers": {
    "Authorization": "Bearer <webhook_secret_token>"
  },
  "enabled": true,
  "debug": false,
  "trigger_fields": [
    "project.actions"
  ],
  "payload_fields": [
    "project.id",
    "project.identifier",
    "project.title",
    "project.address",
    "project.contacts_data.email",
    "project.contacts_data.first_name",
    "project.contacts_data.family_name",
    "project.contacts_data.phone",
    "project.actions",
    "project.stage"
  ]
}
```

### 4.2 Script de Configuración

```python
import requests
import os

def setup_opensolar_webhook():
    """
    Configurar webhook en OpenSolar
    """
    token = os.getenv('OPENSOLAR_TOKEN')
    org_id = os.getenv('OPENSOLAR_ORG_ID')
    webhook_url = os.getenv('WEBHOOK_URL')
    webhook_secret = os.getenv('WEBHOOK_SECRET')
    
    url = f"https://api.opensolar.com/api/orgs/{org_id}/webhooks/"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "endpoint": webhook_url,
        "headers": json.dumps({
            "Authorization": f"Bearer {webhook_secret}"
        }),
        "enabled": True,
        "debug": False,
        "trigger_fields": ["project.actions"],
        "payload_fields": [
            "project.id",
            "project.identifier",
            "project.title",
            "project.address",
            "project.contacts_data.*",
            "project.actions",
            "project.stage"
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    return response.json()
```

---

## 5. Lógica de Triggers y Monitoreo

### 5.1 Identificación de Acciones Clave

```python
# Mapeo de acciones importantes y sus descripciones
ACTION_DESCRIPTIONS = {
    "pago de cuota inicial": {
        "title": "Pago de Cuota Inicial Recibido",
        "description": "Hemos recibido exitosamente el pago de tu cuota inicial. Tu proyecto solar está oficialmente en marcha.",
        "next_steps": "Nuestro equipo técnico realizará una visita al sitio para confirmar las especificaciones del diseño.",
        "is_trigger": True  # Esta acción activa las notificaciones
    },
    "visita tecnica": {
        "title": "Visita Técnica Completada",
        "description": "Nuestro equipo técnico ha completado la visita a tu propiedad y ha verificado todos los detalles necesarios para la instalación.",
        "next_steps": "Procederemos con la preparación de los documentos finales y la programación de la instalación."
    },
    "of aprobada": {
        "title": "Oferta en Firme Aprobada",
        "description": "Tu oferta en firme ha sido aprobada. Todos los detalles técnicos y financieros están confirmados.",
        "next_steps": "Iniciaremos los trámites administrativos y la adquisición de los equipos."
    },
    "agendar instalación": {
        "title": "Instalación Programada",
        "description": "Hemos programado la fecha de instalación de tu sistema solar.",
        "next_steps": "Te contactaremos para confirmar la fecha y preparar el sitio para la instalación."
    },
    "instalación realizada": {
        "title": "Instalación Completada",
        "description": "¡Felicitaciones! La instalación de tu sistema solar ha sido completada exitosamente.",
        "next_steps": "Realizaremos las pruebas finales y la conexión a la red eléctrica."
    }
}

def get_action_description(action_title):
    """
    Obtener descripción de una acción basada en su título
    """
    action_key = action_title.lower().strip()
    
    for key, info in ACTION_DESCRIPTIONS.items():
        if key in action_key:
            return info
    
    # Descripción genérica si no se encuentra
    return {
        "title": f"Actualización: {action_title}",
        "description": f"Se ha completado la acción '{action_title}' en tu proyecto solar.",
        "next_steps": "Nuestro equipo continuará trabajando en las siguientes etapas del proyecto."
    }
```

### 5.2 Verificación de Primera Notificación

```python
def check_if_first_notification(project_id):
    """
    Verificar si es la primera notificación para este proyecto
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM notifications WHERE project_id = ?",
        (project_id,)
    )
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count == 0

def is_initial_payment_action(action):
    """
    Verificar si la acción es el pago de cuota inicial
    """
    action_title = action['title'].lower().strip()
    
    keywords = ['pago', 'cuota inicial', 'inicial', 'anticipo']
    
    return any(keyword in action_title for keyword in keywords)
```

### 5.3 Detección de Acciones Completadas Recientemente

```python
from datetime import datetime, timedelta

def get_recently_completed_actions(actions):
    """
    Obtener acciones que se completaron en las últimas 24 horas
    """
    recently_completed = []
    now = datetime.utcnow()
    threshold = now - timedelta(hours=24)
    
    for action in actions:
        events = action.get('events', [])
        
        for event in events:
            if not event.get('is_complete'):
                continue
            
            completion_date_str = event.get('completion_date')
            if not completion_date_str:
                continue
            
            # Parsear fecha de completación
            completion_date = datetime.fromisoformat(
                completion_date_str.replace('Z', '+00:00')
            )
            
            # Si se completó recientemente
            if completion_date >= threshold:
                recently_completed.append({
                    'action': action,
                    'event': event,
                    'completion_date': completion_date
                })
                break  # Solo el evento más reciente por acción
    
    return recently_completed
```

---

## 6. Despliegue y Configuración

### 6.1 Variables de Entorno

```bash
# OpenSolar API
OPENSOLAR_TOKEN=s_RYGBQBBHFODJJ6ESTGS5AQ7GN444UR7K
OPENSOLAR_ORG_ID=80856

# Gmail API
GMAIL_CLIENT_ID=<client_id>
GMAIL_CLIENT_SECRET=<client_secret>
GMAIL_REFRESH_TOKEN=<refresh_token>

# Webhook
WEBHOOK_SECRET=<random_secret_token>
WEBHOOK_URL=https://notificaciones-greenhproject.onrender.com/webhook/opensolar

# Base de datos
DATABASE_URL=sqlite:///notifications.db

# Configuración general
FLASK_ENV=production
FLASK_SECRET_KEY=<random_secret_key>
```

### 6.2 Despliegue en Render

**Archivo:** `render.yaml`

```yaml
services:
  - type: web
    name: notificaciones-greenhproject
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: OPENSOLAR_TOKEN
        sync: false
      - key: OPENSOLAR_ORG_ID
        sync: false
      - key: GMAIL_CLIENT_ID
        sync: false
      - key: GMAIL_CLIENT_SECRET
        sync: false
      - key: GMAIL_REFRESH_TOKEN
        sync: false
      - key: WEBHOOK_SECRET
        sync: false
```

### 6.3 Estructura del Proyecto

```
notificaciones-automaticas/
├── app.py                      # Aplicación Flask principal
├── config.py                   # Configuración
├── requirements.txt            # Dependencias
├── render.yaml                 # Configuración de Render
├── .env.example               # Ejemplo de variables de entorno
├── database/
│   ├── __init__.py
│   ├── models.py              # Modelos de base de datos
│   └── init_db.py             # Script de inicialización
├── services/
│   ├── __init__.py
│   ├── opensolar.py           # Integración con OpenSolar
│   ├── gmail_service.py       # Integración con Gmail
│   └── notification_service.py # Lógica de notificaciones
├── templates/
│   ├── email_first_notification.html
│   ├── email_progress_update.html
│   └── email_base.html
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Validadores
│   └── helpers.py             # Funciones auxiliares
└── tests/
    ├── __init__.py
    ├── test_webhook.py
    └── test_notifications.py
```

---

## 7. Seguridad y Consideraciones

### 7.1 Seguridad

1. **Autenticación del Webhook:**
   - Validar token secreto en cada request
   - Verificar origen del webhook

2. **Protección de Datos:**
   - No almacenar contraseñas en la base de datos
   - Encriptar datos sensibles
   - Usar HTTPS para todas las comunicaciones

3. **Rate Limiting:**
   - Limitar requests por IP
   - Prevenir abuse del endpoint

### 7.2 Monitoreo y Logs

1. **Logging:**
   - Registrar todos los webhooks recibidos
   - Logs de emails enviados
   - Errores y excepciones

2. **Alertas:**
   - Notificar si el servicio está caído
   - Alertar si hay muchos errores consecutivos

### 7.3 Manejo de Errores

```python
def send_notification_with_retry(notification_data, max_retries=3):
    """
    Enviar notificación con reintentos en caso de error
    """
    for attempt in range(max_retries):
        try:
            send_email_via_gmail(**notification_data)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                # Último intento fallido, registrar error
                log_error(notification_data, str(e))
                return False
            
            # Esperar antes de reintentar
            time.sleep(2 ** attempt)  # Backoff exponencial
    
    return False
```

---

## 8. Testing y Validación

### 8.1 Tests Unitarios

```python
def test_webhook_processing():
    """Test procesamiento de webhook"""
    webhook_data = {
        "data": {
            "project": {
                "id": 123,
                "actions": [...]
            }
        }
    }
    
    result = process_webhook(webhook_data)
    assert result['status'] == 'success'

def test_email_generation():
    """Test generación de emails"""
    email = generate_first_notification_email(
        client_data={'first_name': 'Juan'},
        project_data={},
        action_data={}
    )
    
    assert 'Juan' in email['html']
    assert 'greenhproject.com' in email['html']
```

### 8.2 Testing Manual

1. **Simular webhook de OpenSolar:**
   ```bash
   curl -X POST https://localhost:5000/webhook/opensolar \
     -H "Authorization: Bearer <webhook_secret>" \
     -H "Content-Type: application/json" \
     -d @test_webhook.json
   ```

2. **Verificar email recibido**
3. **Revisar logs y base de datos**

---

## 9. Mantenimiento y Escalabilidad

### 9.1 Mantenimiento

- **Backups:** Realizar backups diarios de la base de datos
- **Actualizaciones:** Mantener dependencias actualizadas
- **Monitoreo:** Revisar logs semanalmente

### 9.2 Escalabilidad

Si el volumen de notificaciones crece:

1. **Queue System:** Implementar Redis + Celery para procesamiento asíncrono
2. **Base de datos:** Migrar a PostgreSQL
3. **Caching:** Implementar cache para templates
4. **Load Balancing:** Múltiples instancias del servicio

---

## 10. Cronograma de Implementación

### Fase 1: Desarrollo (Estimado: 2-3 días)
- ✅ Investigación de API (Completado)
- ⏭️ Desarrollo del backend Flask
- ⏭️ Implementación de integración con OpenSolar
- ⏭️ Implementación de integración con Gmail

### Fase 2: Templates y Diseño (Estimado: 1 día)
- ⏭️ Diseño de templates HTML
- ⏭️ Implementación de templates en Jinja2
- ⏭️ Pruebas de diseño en diferentes clientes de email

### Fase 3: Testing (Estimado: 1 día)
- ⏭️ Tests unitarios
- ⏭️ Tests de integración
- ⏭️ Testing manual con datos reales

### Fase 4: Despliegue (Estimado: 1 día)
- ⏭️ Configuración en Render
- ⏭️ Configuración de webhook en OpenSolar
- ⏭️ Configuración de Gmail API
- ⏭️ Pruebas en producción

### Fase 5: Documentación y Entrega (Estimado: 1 día)
- ⏭️ Documentación técnica
- ⏭️ Manual de usuario
- ⏭️ Entrega al cliente

**Total estimado: 6-7 días**

---

## 11. Conclusiones

Este sistema de notificaciones automáticas proporcionará una experiencia profesional y transparente para los clientes de GreenH Project, manteniéndolos informados en cada etapa de su proyecto solar. La arquitectura propuesta es escalable, mantenible y utiliza tecnologías modernas y confiables.

### Beneficios clave:
- ✅ Comunicación automática y oportuna con clientes
- ✅ Reducción de carga de trabajo manual
- ✅ Mejora en la experiencia del cliente
- ✅ Trazabilidad completa de notificaciones
- ✅ Diseño profesional y estético
- ✅ Integración perfecta con OpenSolar

---

**Documento preparado por:** Manus AI  
**Para:** GreenH Project  
**Fecha:** 04 de octubre de 2025
