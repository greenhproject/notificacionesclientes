# Guía de Despliegue en Render
## Sistema de Notificaciones Automáticas - Green House Project

Esta guía te llevará paso a paso para desplegar el sistema de notificaciones automáticas en Render.

---

## 📋 Requisitos Previos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en GitHub (para subir el código)
- ✅ Cuenta en Render (gratis en https://render.com)
- ✅ Token de API de OpenSolar
- ✅ Acceso a la cuenta admin@greenhproject.com

---

## 🚀 Paso 1: Subir el Código a GitHub

### 1.1 Crear un repositorio en GitHub

1. Ve a https://github.com y haz login
2. Click en el botón **"New"** (o el ícono +)
3. Nombre del repositorio: `notificaciones-greenhproject`
4. Descripción: "Sistema de notificaciones automáticas para clientes de Green House Project"
5. Selecciona **Private** (repositorio privado)
6. NO marques "Initialize this repository with a README"
7. Click en **"Create repository"**

### 1.2 Subir el código

Desde tu computadora, en la carpeta del proyecto:

```bash
cd notificaciones-automaticas

# Inicializar git (si no está inicializado)
git init

# Agregar todos los archivos
git add .

# Hacer el primer commit
git commit -m "Sistema de notificaciones automáticas - versión inicial"

# Conectar con GitHub (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/notificaciones-greenhproject.git

# Subir el código
git branch -M main
git push -u origin main
```

**Nota**: GitHub te pedirá autenticación. Usa un Personal Access Token si es necesario.

---

## 🌐 Paso 2: Crear Cuenta en Render

1. Ve a https://render.com
2. Click en **"Get Started"**
3. Puedes registrarte con:
   - GitHub (recomendado)
   - GitLab
   - Email
4. Completa el registro
5. Verifica tu email

---

## ⚙️ Paso 3: Crear el Servicio Web en Render

### 3.1 Conectar GitHub con Render

1. En el dashboard de Render, click en **"New +"**
2. Selecciona **"Web Service"**
3. Click en **"Connect account"** junto a GitHub
4. Autoriza a Render para acceder a tus repositorios
5. Selecciona el repositorio `notificaciones-greenhproject`

### 3.2 Configurar el servicio

Render detectará automáticamente que es una aplicación Python. Configura:

**Configuración básica:**
- **Name**: `notificaciones-greenhproject` (o el nombre que prefieras)
- **Region**: `Oregon (US West)` (o la más cercana)
- **Branch**: `main`
- **Root Directory**: (dejar vacío)
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`

**Plan:**
- Selecciona **"Free"** (gratis)

### 3.3 Configurar Variables de Entorno

Antes de hacer el deploy, configura las variables de entorno. Click en **"Advanced"** y luego **"Add Environment Variable"**:

Agrega las siguientes variables:

| Key | Value | Notas |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Versión de Python |
| `FLASK_ENV` | `production` | Ambiente de Flask |
| `FLASK_SECRET_KEY` | `[genera una clave aleatoria]` | Usa un generador de claves |
| `OPENSOLAR_TOKEN` | `[tu token de OpenSolar]` | Obtener de OpenSolar |
| `OPENSOLAR_ORG_ID` | `80856` | ID de tu organización |
| `WEBHOOK_SECRET` | `[genera un secreto aleatorio]` | Guárdalo, lo necesitarás |
| `DATABASE_URL` | `sqlite:///notifications.db` | Base de datos SQLite |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

**Cómo generar claves aleatorias:**

```bash
# En tu terminal:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Ejecuta este comando dos veces para generar:
1. `FLASK_SECRET_KEY`
2. `WEBHOOK_SECRET`

**Cómo obtener el token de OpenSolar:**

1. Inicia sesión en OpenSolar con greenhproject@gmail.com
2. Ve a Settings > API
3. Crea un nuevo token o usa uno existente
4. Copia el token y pégalo en `OPENSOLAR_TOKEN`

### 3.4 Desplegar

1. Revisa que todas las variables estén configuradas
2. Click en **"Create Web Service"**
3. Render comenzará a construir y desplegar tu aplicación
4. Espera 2-5 minutos mientras se despliega

**Verás logs en tiempo real:**
```
==> Building...
==> Installing dependencies...
==> Starting application...
==> Deploy successful!
```

5. Una vez completado, verás un mensaje: **"Your service is live 🎉"**
6. Anota la URL de tu aplicación, será algo como:
   ```
   https://notificaciones-greenhproject.onrender.com
   ```

---

## 🔗 Paso 4: Configurar el Webhook en OpenSolar

Ahora que tu aplicación está desplegada, configura el webhook en OpenSolar.

### 4.1 Preparar la información

Necesitarás:
- **Webhook URL**: `https://TU-APP.onrender.com/webhook/opensolar`
- **Webhook Secret**: El que generaste en las variables de entorno

### 4.2 Opción A: Usar el script automatizado

Desde tu computadora:

```bash
cd notificaciones-automaticas

# Configurar variables de entorno
export OPENSOLAR_TOKEN="tu-token-aqui"
export WEBHOOK_SECRET="tu-secreto-aqui"
export WEBHOOK_URL="https://TU-APP.onrender.com/webhook/opensolar"

# Ejecutar el script
python3 setup_webhook.py
```

### 4.2 Opción B: Configuración manual en OpenSolar

1. Inicia sesión en OpenSolar (greenhproject@gmail.com)
2. Ve a **Settings** > **Integrations** > **Webhooks**
3. Click en **"Create Webhook"**
4. Configura:

**Webhook Configuration:**
- **Endpoint URL**: `https://TU-APP.onrender.com/webhook/opensolar`
- **Enabled**: ✅ Marcado
- **Authentication**: Bearer Token
- **Token**: Tu `WEBHOOK_SECRET`

**Trigger Configuration:**
- **Model**: `project`
- **Actions**: `update`
- **Trigger Fields**: `project.actions`

**Payload Configuration:**
Selecciona los siguientes campos:
- `project.id`
- `project.identifier`
- `project.title`
- `project.address`
- `project.contacts_data.*`
- `project.actions`
- `project.stage`

5. Click en **"Save"** o **"Create"**

---

## 🧪 Paso 5: Probar el Sistema

### 5.1 Verificar que la aplicación está funcionando

1. Abre tu navegador
2. Ve a: `https://TU-APP.onrender.com/health`
3. Deberías ver:
   ```json
   {
     "status": "ok",
     "timestamp": "2025-10-04T..."
   }
   ```

### 5.2 Probar con un proyecto real

1. Inicia sesión en OpenSolar
2. Abre un proyecto de prueba
3. Ve a la sección de **Actions** o **Workflow**
4. Marca como completada la acción **"Pago de cuota inicial"**
5. Espera 10-30 segundos

### 5.3 Verificar que el email se envió

1. Revisa la bandeja de entrada del cliente (o admin@greenhproject.com si es prueba)
2. Deberías recibir un email con:
   - Asunto: "¡Bienvenido a Green House Project! - Acceso a tu Portal de Cliente"
   - Logo de Green House Project
   - Credenciales de acceso al portal
   - ID del proyecto (sin prefijo GHP-)
   - Botón para copiar el ID

### 5.4 Revisar los logs en Render

1. Ve al dashboard de Render
2. Click en tu servicio `notificaciones-greenhproject`
3. Ve a la pestaña **"Logs"**
4. Busca mensajes como:
   ```
   Webhook recibido: project, update
   Procesando proyecto ID: 7772938
   Email enviado exitosamente a cliente@email.com
   ```

---

## 🔧 Paso 6: Configuración de Gmail (Importante)

**NOTA IMPORTANTE**: El sistema actual usa la función integrada de Gmail de Manus, que tiene limitaciones para renderizar HTML.

Para que los emails se envíen correctamente con formato HTML en producción, necesitas configurar uno de estos métodos:

### Opción A: Gmail API (Recomendado)

1. Ve a Google Cloud Console
2. Crea un proyecto nuevo
3. Habilita la Gmail API
4. Crea credenciales OAuth 2.0
5. Descarga el archivo de credenciales
6. Agrega las credenciales como variables de entorno en Render

### Opción B: SendGrid (Más fácil)

1. Crea una cuenta en SendGrid (gratis hasta 100 emails/día)
2. Obtén tu API Key
3. Modifica `services/gmail_service.py` para usar SendGrid
4. Agrega `SENDGRID_API_KEY` a las variables de entorno

### Opción C: Mailgun

Similar a SendGrid, pero con diferentes límites gratuitos.

**Por ahora, el sistema funcionará pero los emails pueden no renderizarse correctamente. Esto se solucionará con una de las opciones anteriores.**

---

## 📊 Paso 7: Monitoreo y Mantenimiento

### 7.1 Revisar logs regularmente

- Ve a Render > Tu servicio > Logs
- Busca errores o warnings
- Verifica que los webhooks se reciban correctamente

### 7.2 Base de datos

La base de datos SQLite se almacena en el disco del servidor. Para consultar notificaciones:

```python
from database import Database, Notification

db = Database()
notification_model = Notification(db)

# Ver todas las notificaciones
notifications = notification_model.get_all()
for n in notifications:
    print(f"Proyecto: {n['project_id']}, Email: {n['recipient_email']}, Estado: {n['status']}")
```

### 7.3 Actualizar el código

Cuando hagas cambios:

```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

Render detectará automáticamente los cambios y redesplegará la aplicación.

---

## ❓ Solución de Problemas

### Problema: El webhook no recibe notificaciones

**Solución:**
1. Verifica que el webhook esté habilitado en OpenSolar
2. Revisa que la URL sea correcta
3. Verifica que el `WEBHOOK_SECRET` coincida
4. Revisa los logs en Render

### Problema: Los emails no se envían

**Solución:**
1. Verifica que la cuenta de Gmail esté configurada
2. Revisa los logs para ver errores específicos
3. Verifica que el email del cliente sea válido
4. Considera usar SendGrid o Mailgun

### Problema: La aplicación no inicia

**Solución:**
1. Revisa los logs de build en Render
2. Verifica que todas las dependencias estén en `requirements.txt`
3. Verifica que las variables de entorno estén configuradas
4. Asegúrate de que el comando de inicio sea correcto

### Problema: Error 503 o 504

**Solución:**
1. El plan gratuito de Render "duerme" después de 15 minutos de inactividad
2. La primera petición después de dormir puede tardar 30-60 segundos
3. Considera actualizar al plan pagado si necesitas disponibilidad 24/7

---

## 🎉 ¡Listo!

Tu sistema de notificaciones automáticas está desplegado y funcionando. Los clientes recibirán emails automáticamente cuando se completen acciones en sus proyectos.

### Próximos pasos recomendados:

1. ✅ Probar con varios proyectos reales
2. ✅ Configurar SendGrid o Gmail API para emails HTML
3. ✅ Personalizar las descripciones de acciones en `config.py`
4. ✅ Agregar más tipos de notificaciones si es necesario
5. ✅ Configurar alertas de errores (opcional)

---

## 📞 Soporte

Si tienes problemas:
1. Revisa esta guía nuevamente
2. Consulta la documentación en `README.md`
3. Revisa los logs en Render
4. Contacta al equipo de soporte

**¡Éxito con tu sistema de notificaciones!** 🚀
