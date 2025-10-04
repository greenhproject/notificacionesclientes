# Sistema de Notificaciones Automáticas
## Green House Project - Integración con OpenSolar

Sistema automatizado para enviar notificaciones por email a clientes cuando se completan acciones en sus proyectos solares en OpenSolar.

---

## 📋 Descripción

Este sistema monitorea los cambios en los proyectos de OpenSolar y envía automáticamente emails profesionales y estéticos a los clientes cada vez que se completa una acción importante en su proyecto. Las notificaciones comienzan a partir del pago de la cuota inicial y continúan durante todo el ciclo de vida del proyecto.

### Características principales:

- ✅ Notificaciones automáticas por email cuando cambia el estado de acciones
- ✅ Inicio de notificaciones a partir del pago de cuota inicial
- ✅ Diseño profesional y limpio con colores corporativos
- ✅ Credenciales de acceso al portal de clientes en el primer email
- ✅ Descripciones claras de cada actualización del proyecto
- ✅ Integración completa con OpenSolar API
- ✅ Base de datos para registro de notificaciones enviadas
- ✅ Sistema de reintentos en caso de errores

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                          OpenSolar                              │
│                    (Sistema de Gestión)                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Webhook POST
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend Flask (Webhook Receiver)                   │
│  - Recibe webhooks de OpenSolar                                 │
│  - Identifica acciones completadas                              │
│  - Genera contenido de emails                                   │
│  - Envía emails vía Gmail                                       │
│  - Registra notificaciones en BD                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Gmail API
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Cliente Final                           │
│                    (Recibe notificaciones)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
notificaciones-automaticas/
├── app.py                          # Aplicación Flask principal
├── config.py                       # Configuración
├── requirements.txt                # Dependencias Python
├── render.yaml                     # Configuración para Render
├── Procfile                        # Configuración para Railway/Heroku
├── .env.example                    # Ejemplo de variables de entorno
├── .gitignore                      # Archivos ignorados por Git
├── README.md                       # Este archivo
├── arquitectura.md                 # Documentación detallada de arquitectura
├── setup_webhook.py                # Script para configurar webhook en OpenSolar
├── test_notification_system.py    # Script de pruebas
├── test_email_html.py              # Script de prueba de emails HTML
│
├── database/
│   ├── __init__.py
│   └── models.py                   # Modelos de base de datos
│
├── services/
│   ├── __init__.py
│   ├── opensolar.py                # Integración con OpenSolar API
│   ├── gmail_service.py            # Integración con Gmail
│   └── notification_service.py     # Lógica de notificaciones
│
├── templates/
│   ├── email_base.html             # Template base de emails
│   ├── email_first_notification.html    # Template de bienvenida
│   └── email_progress_update.html  # Template de actualizaciones
│
├── utils/
│   └── (utilidades auxiliares)
│
└── tests/
    └── (tests unitarios)
```

---

## 🚀 Instalación y Configuración

### Requisitos previos:

- Python 3.11+
- Cuenta en OpenSolar con acceso a la API
- Cuenta de Gmail para envío de emails (admin@greenhproject.com)
- Cuenta en Render o Railway para despliegue

### Paso 1: Clonar el repositorio

```bash
git clone <repository-url>
cd notificaciones-automaticas
```

### Paso 2: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3: Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
FLASK_ENV=production
FLASK_SECRET_KEY=<genera-una-clave-secreta-aleatoria>

OPENSOLAR_TOKEN=<tu-token-de-opensolar>
OPENSOLAR_ORG_ID=80856

WEBHOOK_SECRET=<genera-un-secreto-aleatorio>
WEBHOOK_URL=https://tu-app.onrender.com/webhook/opensolar

DATABASE_URL=sqlite:///notifications.db
```

### Paso 4: Inicializar la base de datos

La base de datos se inicializa automáticamente al ejecutar la aplicación por primera vez.

### Paso 5: Ejecutar localmente (opcional)

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

---

## 🌐 Despliegue en Render

### Opción 1: Despliegue automático con render.yaml

1. Crea una cuenta en [Render](https://render.com)
2. Conecta tu repositorio de GitHub
3. Render detectará automáticamente el archivo `render.yaml`
4. Configura las variables de entorno en el dashboard de Render:
   - `OPENSOLAR_TOKEN`
   - `WEBHOOK_SECRET`
5. Despliega la aplicación

### Opción 2: Despliegue manual

1. En Render, crea un nuevo "Web Service"
2. Conecta tu repositorio
3. Configura:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
   - **Environment**: Python 3.11
4. Agrega las variables de entorno
5. Despliega

---

## 🔧 Configuración del Webhook en OpenSolar

Una vez desplegada la aplicación, configura el webhook en OpenSolar:

### Opción 1: Usar el script automatizado

```bash
export OPENSOLAR_TOKEN="tu-token"
export WEBHOOK_SECRET="tu-secreto"
export WEBHOOK_URL="https://tu-app.onrender.com/webhook/opensolar"

python setup_webhook.py
```

### Opción 2: Configuración manual

1. Inicia sesión en OpenSolar
2. Ve a Settings > Integrations > Webhooks
3. Crea un nuevo webhook con:
   - **Endpoint URL**: `https://tu-app.onrender.com/webhook/opensolar`
   - **Headers**: `Authorization: Bearer <tu-webhook-secret>`
   - **Trigger Fields**: `project.actions`
   - **Payload Fields**:
     - `project.id`
     - `project.identifier`
     - `project.title`
     - `project.address`
     - `project.contacts_data.*`
     - `project.actions`
     - `project.stage`
4. Habilita el webhook

---

## 📧 Tipos de Notificaciones

### 1. Primera Notificación (Bienvenida)

**Trigger**: Cuando se marca como completado el pago de cuota inicial

**Contenido**:
- Mensaje de bienvenida
- Confirmación del pago de cuota inicial
- **Credenciales de acceso al portal**:
  - URL: https://www.greenhproject.com/gestionproyectos
  - ID del proyecto
  - Instrucciones de acceso
- Próximos pasos
- Información del proyecto

**Asunto**: "¡Bienvenido a Green House Project! - Acceso a tu Portal de Cliente"

### 2. Actualizaciones de Progreso

**Trigger**: Cuando se completa cualquier acción después de la primera notificación

**Contenido**:
- Descripción de la acción completada
- Contexto y explicación del avance
- Próximos pasos
- Enlace al portal para más detalles
- Información del proyecto

**Asunto**: "Actualización de tu Proyecto Solar - [Nombre de la Acción]"

---

## 🎨 Diseño de Emails

Los emails utilizan un diseño profesional y limpio con:

- **Colores corporativos**: Verde #2E7D32 y #4CAF50
- **Logo de Green House Project**
- **Diseño responsive**: Se adapta a dispositivos móviles
- **Secciones destacadas**: Para información importante
- **Botones de acción**: Para acceder al portal
- **Footer informativo**: Con contacto y copyright

---

## 🔍 Monitoreo y Logs

### Logs de la aplicación

Los logs se guardan en `notifications.log` e incluyen:
- Webhooks recibidos
- Acciones procesadas
- Emails enviados
- Errores y excepciones

### Base de datos

La tabla `notifications` registra:
- Proyecto ID
- Acción completada
- Email del destinatario
- Fecha y hora de envío
- Estado (sent/failed)
- Contenido del email

### Consultar notificaciones de un proyecto

```python
from database import Database, Notification

db = Database()
notification_model = Notification(db)

# Obtener notificaciones de un proyecto
notifications = notification_model.get_by_project(project_id=12345)

for notif in notifications:
    print(f"Acción: {notif['action_title']}")
    print(f"Enviado a: {notif['recipient_email']}")
    print(f"Fecha: {notif['sent_at']}")
    print(f"Estado: {notif['status']}")
    print()
```

---

## 🧪 Pruebas

### Ejecutar pruebas del sistema

```bash
python test_notification_system.py
```

### Probar generación de emails HTML

```bash
python test_email_html.py
```

### Simular un webhook de OpenSolar

```bash
curl -X POST https://tu-app.onrender.com/webhook/opensolar \
  -H "Authorization: Bearer tu-webhook-secret" \
  -H "Content-Type: application/json" \
  -d @test_webhook.json
```

---

## 📝 Acciones Configuradas

El sistema reconoce y describe las siguientes acciones:

| Acción en OpenSolar | Título en Email | Trigger Primera Notif. |
|---------------------|-----------------|------------------------|
| Pago de cuota inicial | Pago de Cuota Inicial Recibido | ✅ Sí |
| Visita técnica | Visita Técnica Completada | ❌ No |
| OF aprobada | Oferta en Firme Aprobada | ❌ No |
| Envío de oferta en firme al cliente | Oferta en Firme Enviada | ❌ No |
| Aprobación de OF | Aprobación de Oferta en Firme | ❌ No |
| Radicación de documentos crédito | Documentos de Crédito Radicados | ❌ No |
| Preaprobado de crédito | Crédito Preaprobado | ❌ No |
| Agendar instalación | Instalación Programada | ❌ No |
| Instalación realizada | Instalación Completada | ❌ No |

Puedes agregar más acciones editando el diccionario `ACTION_DESCRIPTIONS` en `config.py`.

---

## 🔒 Seguridad

### Autenticación del Webhook

Todos los requests al endpoint `/webhook/opensolar` deben incluir el header:

```
Authorization: Bearer <WEBHOOK_SECRET>
```

### Variables de entorno sensibles

Nunca subas al repositorio:
- Tokens de API
- Secretos de webhook
- Credenciales de Gmail
- Claves secretas de Flask

Usa variables de entorno o servicios de gestión de secretos.

### HTTPS

El sistema debe desplegarse con HTTPS habilitado (Render lo proporciona automáticamente).

---

## 🐛 Solución de Problemas

### El webhook no recibe notificaciones

1. Verifica que el webhook esté habilitado en OpenSolar
2. Revisa que la URL del webhook sea correcta y accesible
3. Verifica que el `WEBHOOK_SECRET` coincida en ambos lados
4. Revisa los logs de la aplicación

### Los emails no se envían

1. Verifica que el servicio de Gmail esté configurado correctamente
2. Revisa los logs para ver errores específicos
3. Verifica que el email del cliente sea válido
4. Comprueba que la cuenta admin@greenhproject.com tenga permisos

### La base de datos no se crea

1. Verifica que tengas permisos de escritura en el directorio
2. Asegúrate de que `DATABASE_URL` esté configurado correctamente
3. Revisa los logs para errores de inicialización

### Error al obtener datos de OpenSolar

1. Verifica que `OPENSOLAR_TOKEN` sea válido
2. Comprueba que `OPENSOLAR_ORG_ID` sea correcto
3. Revisa que el token no haya expirado

---

## 📚 Documentación Adicional

- **Arquitectura detallada**: Ver `arquitectura.md`
- **API de OpenSolar**: https://developers.opensolar.com
- **Documentación de Flask**: https://flask.palletsprojects.com
- **Render Docs**: https://render.com/docs

---

## 🤝 Soporte

Para soporte técnico o preguntas:
- Email: admin@greenhproject.com
- Documentación del proyecto: Ver `arquitectura.md`

---

## 📄 Licencia

© 2025 Green House Project. Todos los derechos reservados.

---

## 🎯 Próximos Pasos

Después del despliegue:

1. ✅ Desplegar la aplicación en Render
2. ✅ Configurar el webhook en OpenSolar
3. ✅ Probar con un proyecto real
4. ✅ Monitorear los logs durante los primeros días
5. ✅ Ajustar descripciones de acciones según sea necesario
6. ✅ Configurar alertas para errores

---

**Desarrollado por**: Manus AI  
**Para**: Green House Project  
**Fecha**: Octubre 2025
