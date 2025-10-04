# Configuración de Gmail SMTP para Notificaciones Automáticas

## 📋 Requisitos Previos

Para usar Gmail SMTP necesitas:
- Una cuenta de Gmail (admin@greenhproject.com)
- Verificación en dos pasos activada
- Una contraseña de aplicación generada

## 🔐 Paso 1: Activar Verificación en Dos Pasos

1. Ve a tu cuenta de Google: https://myaccount.google.com/
2. En el menú lateral, selecciona **Seguridad**
3. Busca la sección **Cómo inicias sesión en Google**
4. Haz clic en **Verificación en dos pasos**
5. Sigue los pasos para activarla (si no está activada)

## 🔑 Paso 2: Generar Contraseña de Aplicación

1. Una vez activada la verificación en dos pasos, regresa a **Seguridad**
2. Busca **Contraseñas de aplicaciones** (aparece solo si la verificación en dos pasos está activada)
3. Haz clic en **Contraseñas de aplicaciones**
4. Es posible que te pida tu contraseña de Google nuevamente
5. En "Selecciona la app", elige **Correo**
6. En "Selecciona el dispositivo", elige **Otro (nombre personalizado)**
7. Escribe un nombre como "Sistema Notificaciones GHP"
8. Haz clic en **Generar**
9. **Copia la contraseña de 16 caracteres** que aparece (sin espacios)

⚠️ **Importante**: Guarda esta contraseña de forma segura. No podrás verla nuevamente.

## 🔧 Paso 3: Configurar en el Sistema

### Opción A: Configuración Local (Desarrollo)

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Crear archivo .env
cd /home/ubuntu/notificaciones-automaticas
nano .env
```

Agrega las siguientes variables:

```env
# OpenSolar
OPENSOLAR_TOKEN=tu_token_de_opensolar
OPENSOLAR_ORG_ID=80856

# Webhook
WEBHOOK_SECRET=tu_secreto_del_webhook

# Gmail SMTP
GMAIL_SMTP_PASSWORD=tu_contraseña_de_aplicacion_aqui

# Flask
FLASK_ENV=development
FLASK_SECRET_KEY=tu_clave_secreta_aqui
```

### Opción B: Configuración en Render (Producción)

1. Ve a tu dashboard de Render: https://dashboard.render.com/
2. Selecciona tu servicio web (notificaciones-automaticas)
3. Ve a la pestaña **Environment**
4. Agrega una nueva variable de entorno:
   - **Key**: `GMAIL_SMTP_PASSWORD`
   - **Value**: Tu contraseña de aplicación de 16 caracteres
5. Haz clic en **Save Changes**

El servicio se reiniciará automáticamente con la nueva configuración.

## ✅ Paso 4: Probar la Configuración

### Prueba Local

```bash
cd /home/ubuntu/notificaciones-automaticas

# Configurar la contraseña temporalmente
export GMAIL_SMTP_PASSWORD="tu_contraseña_de_aplicacion"

# Ejecutar script de prueba
python3 test_smtp_gmail.py
```

El script te pedirá un email de destino para enviar un correo de prueba.

### Prueba en Producción

Una vez configurada la variable en Render, el sistema enviará correos automáticamente cuando:
1. Se marque el checkbox de pago inicial en OpenSolar
2. Cambie el estado de un proyecto

## 🔍 Verificación de Logs

Para verificar que los correos se están enviando:

### En Render:
1. Ve a tu servicio en Render
2. Haz clic en **Logs**
3. Busca mensajes como:
   - `Conectando a smtp.gmail.com:587`
   - `Autenticando como admin@greenhproject.com`
   - `Email enviado exitosamente a [email]`

### Localmente:
```bash
tail -f notifications.log
```

## ⚠️ Solución de Problemas

### Error: "Username and Password not accepted"

**Causa**: La contraseña de aplicación es incorrecta o la verificación en dos pasos no está activada.

**Solución**:
1. Verifica que la verificación en dos pasos esté activada
2. Genera una nueva contraseña de aplicación
3. Asegúrate de copiar la contraseña completa (16 caracteres sin espacios)

### Error: "SMTPAuthenticationError"

**Causa**: Problemas de autenticación con Gmail.

**Solución**:
1. Verifica que estés usando la contraseña de aplicación, NO tu contraseña normal de Gmail
2. Asegúrate de que no haya espacios en la contraseña
3. Genera una nueva contraseña de aplicación

### Los correos no llegan

**Posibles causas**:
1. El correo está en la carpeta de spam
2. El email del destinatario es incorrecto
3. Hay un problema con la configuración SMTP

**Solución**:
1. Revisa la carpeta de spam del destinatario
2. Verifica los logs para ver si hay errores
3. Ejecuta el script de prueba para verificar la configuración

### Error: "Connection refused"

**Causa**: No se puede conectar al servidor SMTP de Gmail.

**Solución**:
1. Verifica tu conexión a internet
2. Asegúrate de que el puerto 587 no esté bloqueado por un firewall
3. Intenta más tarde (puede ser un problema temporal de Gmail)

## 📧 Formato del Email

Los correos se envían con:
- **Remitente**: Green House Project <admin@greenhproject.com>
- **Formato**: HTML con diseño profesional
- **Contenido**: Información del proyecto y próximos pasos
- **Enlace**: Portal de gestión de proyectos

## 🔒 Seguridad

- ✅ La contraseña de aplicación es específica para esta aplicación
- ✅ Puedes revocarla en cualquier momento sin afectar tu cuenta de Gmail
- ✅ No compartas la contraseña de aplicación públicamente
- ✅ No la subas a repositorios de código (usa variables de entorno)
- ✅ Renuévala periódicamente por seguridad

## 📚 Referencias

- [Contraseñas de aplicaciones de Google](https://support.google.com/accounts/answer/185833)
- [Verificación en dos pasos](https://support.google.com/accounts/answer/185839)
- [Configuración SMTP de Gmail](https://support.google.com/mail/answer/7126229)
