# -*- coding: utf-8 -*-
"""
Aplicación Flask para el sistema de notificaciones automáticas
GreenH Project - OpenSolar Integration
"""

import os
import logging
from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps

# Módulos del proyecto
from config import get_config
from database import Database, Notification
from services import OpenSolarService, GmailService, NotificationService

# ---------------------------------------------------------------------------
# Configuración de Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("notifications.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Inicialización de la Aplicación y Servicios
# ---------------------------------------------------------------------------

# Cargar configuración
config = get_config()

# Inicializar aplicación Flask
app = Flask(__name__)
app.config.from_object(config)

# Inicializar base de datos (opcional - solo si DATABASE_URL está configurada)
try:
    db = Database(config.DATABASE_URL)
    notification_model = Notification(db)
    logger.info("Base de datos inicializada correctamente")
except Exception as e:
    logger.warning(f"No se pudo inicializar la base de datos: {e}")
    logger.warning("La aplicación funcionará sin persistencia de notificaciones")
    db = None
    notification_model = None

# Inicializar servicios
opensolar_service = OpenSolarService(
    api_token=config.OPENSOLAR_TOKEN,
    org_id=config.OPENSOLAR_ORG_ID,
    base_url=config.OPENSOLAR_API_BASE
)

gmail_service = GmailService(
    from_email=config.GMAIL_FROM_EMAIL,
    from_name=config.GMAIL_FROM_NAME
)

notification_service = NotificationService(
    templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
    client_portal_url=config.CLIENT_PORTAL_URL,
    action_descriptions=config.ACTION_DESCRIPTIONS
)

logger.info(f"Aplicación inicializada en modo {os.getenv("FLASK_ENV", "development")}")

# ---------------------------------------------------------------------------
# Decoradores de Autenticación
# ---------------------------------------------------------------------------

def require_webhook_auth(f):
    """Decorador para proteger el endpoint del webhook"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Intentar obtener el secreto de diferentes headers
        webhook_secret = request.headers.get("X-Webhook-Secret")
        auth_header = request.headers.get("Authorization")
        
        # Validar con X-Webhook-Secret (OpenSolar)
        if webhook_secret:
            logger.info(f"Webhook: Secreto recibido: '{webhook_secret}' (len={len(webhook_secret)})")
            logger.info(f"Webhook: Secreto esperado: '{config.WEBHOOK_SECRET}' (len={len(config.WEBHOOK_SECRET)})")
            if webhook_secret == config.WEBHOOK_SECRET:
                return f(*args, **kwargs)
            else:
                logger.warning(f"Webhook: Secreto inválido. Recibido: '{webhook_secret}', Esperado: '{config.WEBHOOK_SECRET}'")
                return jsonify({"error": "Invalid webhook secret"}), 401
        
        # Validar con Authorization Bearer (alternativo)
        if auth_header:
            try:
                auth_type, token = auth_header.split()
                if auth_type.lower() == "bearer" and token == config.WEBHOOK_SECRET:
                    return f(*args, **kwargs)
                else:
                    logger.warning("Webhook: Token inválido")
                    return jsonify({"error": "Invalid token"}), 403
            except ValueError:
                logger.warning("Webhook: Formato de token inválido")
                return jsonify({"error": "Invalid token format"}), 401
        
        # Si no hay ningún header de autenticación
        logger.warning("Webhook: Falta header de autorización")
        return jsonify({"error": "Authorization header is missing"}), 401
        
    return decorated_function

# ---------------------------------------------------------------------------
# Endpoints de la API
# ---------------------------------------------------------------------------

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de health check para verificar que el servicio está activo"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/webhook/opensolar", methods=["POST"])
@require_webhook_auth
def opensolar_webhook():
    """
    Endpoint para recibir webhooks de OpenSolar.
    Procesa los cambios en proyectos y envía notificaciones si es necesario.
    """
    webhook_data = request.get_json()
    
    if not webhook_data:
        logger.error("Webhook: No se recibieron datos JSON")
        return jsonify({"error": "No JSON data received"}), 400
    
    # Log del payload completo para debug
    logger.info(f"Webhook payload completo: {webhook_data}")
    model = webhook_data.get("model")
    event = webhook_data.get("event")
    logger.info(f"Webhook recibido: model={model}, event={event}")
    
    # Procesar eventos de tipo "Event" con acción "CREATE" (cuando se marca una acción como completada)
    if model == "Event" and event == "CREATE":
        logger.info(f"Procesando evento de tipo Event/CREATE")
        
        # Los datos del evento están en "fields"
        event_data = webhook_data.get("fields", {})
        if not event_data:
            logger.error("Webhook: No hay datos de evento en el payload (fields)")
            return jsonify({"error": "No event data in payload"}), 400
        
        # Verificar que el evento esté completado
        is_complete = event_data.get("is_complete", False)
        if not is_complete:
            logger.info("Webhook ignorado: Evento no está completado")
            return jsonify({"status": "ignored", "reason": "Event not complete"}), 200
        
        # Obtener información del proyecto
        project_data_ref = event_data.get("project_data", {})
        project_id = project_data_ref.get("id")
        
        if not project_id:
            logger.error("Webhook: No se encontró ID de proyecto en el evento")
            return jsonify({"error": "No project ID in event"}), 400
        
        logger.info(f"Procesando evento completado para proyecto ID: {project_id}")
        
        # Obtener datos completos del proyecto desde OpenSolar API
        try:
            project_full_data = opensolar_service.get_project(project_id)
            if not project_full_data:
                logger.error(f"No se pudo obtener datos del proyecto {project_id}")
                return jsonify({"error": "Could not fetch project data"}), 500
        except Exception as e:
            logger.error(f"Error al obtener proyecto {project_id}: {str(e)}")
            return jsonify({"error": f"Error fetching project: {str(e)}"}), 500
        
        # Extraer datos del cliente
        client_data = opensolar_service.extract_client_data(project_full_data)
        if not client_data or not client_data.get("email"):
            logger.error(f"Proyecto {project_id}: No se encontraron datos de contacto o email del cliente")
            return jsonify({"error": "Client contact data or email is missing"}), 400
        
        # Obtener información de la acción completada
        action_title = event_data.get("title", "Acción")
        action_url = event_data.get("action", "")
        completion_date = event_data.get("completion_date")
        
        # Construir objeto de acción simulado para compatibilidad
        action_info = {
            "action": {
                "id": event_data.get("id"),
                "title": action_title,
                "url": action_url
            },
            "event": {
                "is_complete": True,
                "completion_date": completion_date
            },
            "completion_date": completion_date
        }
        
        # Verificar si es la primera notificación para este proyecto
        is_first_notification_for_project = notification_model.check_if_first_notification(project_id) if notification_model else True
        
        # Determinar si es la acción que dispara la primera notificación
        is_trigger_action = opensolar_service.is_initial_payment_action(
            action_info["action"], config.TRIGGER_ACTIONS
        )
        
        email_content = None
        email_type = "progress_update"
        
        # Generar email de primera notificación
        if is_first_notification_for_project and is_trigger_action:
            logger.info(f"Proyecto {project_id}: Generando primera notificación")
            email_content = notification_service.generate_first_notification_email(
                client_data, project_full_data, action_info
            )
            email_type = "first_notification"
        else:
            # Generar email de actualización de progreso
            logger.info(f"Proyecto {project_id}: Generando notificación de progreso")
            email_content = notification_service.generate_progress_update_email(
                client_data, project_full_data, action_info
            )
        
        # Enviar email
        try:
            success = notification_service.send_email(
                to_email=client_data["email"],
                subject=email_content["subject"],
                html_body=email_content["html"],
                text_body=email_content["text"]
            )
            
            if success:
                logger.info(f"Email enviado exitosamente a {client_data['email']}")
                
                # Registrar notificación en la base de datos
                if notification_model:
                    notification_model.log_notification(
                        project_id=project_id,
                        action_id=action_info["action"]["id"],
                        email=client_data["email"],
                        notification_type=email_type
                    )
                
                return jsonify({"status": "success", "email_sent": True}), 200
            else:
                logger.error(f"Error al enviar email a {client_data['email']}")
                return jsonify({"status": "error", "message": "Failed to send email"}), 500
                
        except Exception as e:
            logger.error(f"Error al procesar notificación: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    
    # Ignorar otros tipos de webhooks
    logger.info(f"Webhook ignorado: model={model}, event={event}")
    return jsonify({"status": "ignored", "reason": f"Not a relevant webhook (model={model}, event={event})"}), 200
    
    # 1. Obtener acciones completadas recientemente
    actions = project_data.get("actions", [])
    completed_actions = opensolar_service.get_recently_completed_actions(
        actions,
        threshold_hours=config.RECENT_COMPLETION_THRESHOLD.total_seconds() / 3600
    )
    
    if not completed_actions:
        logger.info(f"Proyecto {project_id}: No hay acciones completadas recientemente")
        return jsonify({"status": "no_actions_to_notify"}), 200
    
    logger.info(f"Proyecto {project_id}: {len(completed_actions)} acciones completadas encontradas")
    
    # 2. Obtener datos del cliente
    client_data = opensolar_service.extract_client_data(project_data)
    if not client_data or not client_data.get("email"):
        logger.error(f"Proyecto {project_id}: No se encontraron datos de contacto o email del cliente")
        return jsonify({"error": "Client contact data or email is missing"}), 400
    
    # 3. Verificar si es la primera notificación para este proyecto
    is_first_notification_for_project = notification_model.check_if_first_notification(project_id) if notification_model else True
    
    notifications_sent = 0
    
    # 4. Procesar cada acción completada
    for action_info in completed_actions:
        action = action_info["action"]
        action_id = action["id"]
        action_title = action["title"]
        
        # Verificar si ya notificamos esta acción
        if notification_model and notification_model.check_if_notified(project_id, action_id):
            logger.info(f"Proyecto {project_id}, Acción {action_id}: Ya notificada, omitiendo")
            continue
        
        # Determinar si es la acción que dispara la primera notificación
        is_trigger_action = opensolar_service.is_initial_payment_action(
            action, config.TRIGGER_ACTIONS
        )
        
        email_content = None
        email_type = "progress_update"
        
        # Generar email de primera notificación
        if is_first_notification_for_project and is_trigger_action:
            logger.info(f"Proyecto {project_id}: Generando primera notificación")
            email_content = notification_service.generate_first_notification_email(
                client_data, project_data, action_info
            )
            email_type = "first_notification"
            is_first_notification_for_project = False # Para no repetir en el mismo webhook
        
        # Generar email de actualización de progreso (si no es la primera)
        elif not notification_model or not notification_model.check_if_first_notification(project_id):
            logger.info(f"Proyecto {project_id}: Generando actualización de progreso")
            email_content = notification_service.generate_progress_update_email(
                client_data, project_data, action_info
            )
        
        # Si no se debe enviar email, continuar
        if not email_content:
            logger.info(f"Proyecto {project_id}, Acción {action_id}: No se requiere notificación en este momento")
            continue
        
        # 5. Enviar email
        success = gmail_service.send_email_with_retry(
            to=client_data["email"],
            subject=email_content["subject"],
            html_body=email_content["html"],
            plain_body=email_content["plain"],
            max_retries=config.NOTIFICATION_RETRY_ATTEMPTS
        )
        
        # 6. Registrar notificación en la base de datos (si está disponible)
        if notification_model:
            status = "sent" if success else "failed"
            error_message = None if success else "Failed to send email after retries"
            
            notification_model.create(
                project_id=project_id,
                project_identifier=project_data.get("identifier"),
                project_title=project_data.get("title"),
                action_id=action_id,
                action_title=action_title,
                recipient_email=client_data["email"],
                recipient_name=client_data.get("full_name"),
                email_type=email_type,
                email_subject=email_content["subject"],
                email_body=email_content["html"],
                webhook_data=webhook_data,
                status=status,
                error_message=error_message
            )
        
        if success:
            notifications_sent += 1
            logger.info(f"Proyecto {project_id}, Acción {action_id}: Notificación enviada a {client_data["email"]}")
        else:
            logger.error(f"Proyecto {project_id}, Acción {action_id}: Fallo al enviar notificación a {client_data["email"]}")

    return jsonify({
        "status": "success",
        "notifications_sent": notifications_sent
    }), 200

# ---------------------------------------------------------------------------
# Bloque Principal de Ejecución
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Usar Waitress como servidor de producción en lugar del de desarrollo de Flask
    from waitress import serve
    serve(app, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

