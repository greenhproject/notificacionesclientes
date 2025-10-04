"""
Servicio de lógica de notificaciones
"""

import logging
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para generar y gestionar notificaciones"""
    
    def __init__(self, templates_dir: str, client_portal_url: str, action_descriptions: Dict):
        """
        Inicializar servicio de notificaciones
        
        Args:
            templates_dir: Directorio donde están los templates de email
            client_portal_url: URL del portal de clientes
            action_descriptions: Mapeo de acciones a descripciones
        """
        self.client_portal_url = client_portal_url
        self.action_descriptions = action_descriptions
        
        # Configurar Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _format_completion_date(self, date_str: str) -> str:
        """
        Formatear fecha de completación desde string ISO a formato legible
        
        Args:
            date_str: Fecha en formato ISO string (ej: "2025-10-04T21:34:27.540111Z")
            
        Returns:
            Fecha formateada (ej: "04 de Octubre de 2025") o string vacío si hay error
        """
        if not date_str:
            return ''
        
        try:
            # Parsear fecha ISO
            date_str_clean = date_str.replace('Z', '+00:00')
            date_obj = datetime.fromisoformat(date_str_clean)
            
            # Formatear en español
            meses = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            
            return f"{date_obj.day:02d} de {meses[date_obj.month]} de {date_obj.year}"
        except Exception as e:
            logger.warning(f"Error al formatear fecha '{date_str}': {e}")
            return date_str  # Devolver la fecha original si hay error
    
    def generate_first_notification_email(self, client_data: Dict, 
                                         project_data: Dict,
                                         action_data: Dict) -> Dict:
        """
        Generar email de primera notificación (pago de cuota inicial)
        
        Args:
            client_data: Datos del cliente (nombre, email, teléfono)
            project_data: Datos del proyecto (ID, título, dirección)
            action_data: Datos de la acción completada
            
        Returns:
            Dict con subject, html y text del email
        """
        # Obtener información de la acción
        action_info = self._get_action_info(action_data)
        
        # Preparar datos para el template
        template_data = {
            'client_name': client_data.get('name', 'Cliente'),
            'project_id': project_data.get('id', ''),
            'project_title': project_data.get('title', ''),
            'project_address': project_data.get('address', ''),
            'action_title': action_info['title'],
            'action_description': action_info['description'],
            'next_steps': action_info['next_steps'],
            'portal_url': self.client_portal_url,
            'completion_date': self._format_completion_date(action_data.get('completion_date', '')),
            'year': '2025'
        }
        
        # Renderizar template HTML
        template = self.jinja_env.get_template('email_first_notification.html')
        html_body = template.render(**template_data)
        
        # Generar versión texto plano
        text_body = self._generate_text_version(template_data, is_first=True)
        
        # Generar asunto
        subject = f"¡Bienvenido a Green House Project! - Acceso a tu Portal de Cliente"
        
        return {
            'subject': subject,
            'html': html_body,
            'text': text_body
        }
    
    def generate_progress_update_email(self, client_data: Dict,
                                      project_data: Dict,
                                      action_data: Dict) -> Dict:
        """
        Generar email de actualización de progreso
        
        Args:
            client_data: Datos del cliente
            project_data: Datos del proyecto
            action_data: Datos de la acción completada
            
        Returns:
            Dict con subject, html y text del email
        """
        # Obtener información de la acción
        action_info = self._get_action_info(action_data)
        
        # Preparar datos para el template
        template_data = {
            'client_name': client_data.get('name', 'Cliente'),
            'project_id': project_data.get('id', ''),
            'project_title': project_data.get('title', ''),
            'project_address': project_data.get('address', ''),
            'action_title': action_info['title'],
            'action_description': action_info['description'],
            'next_steps': action_info['next_steps'],
            'portal_url': self.client_portal_url,
            'completion_date': self._format_completion_date(action_data.get('completion_date', '')),
            'year': '2025'
        }
        
        # Renderizar template HTML
        template = self.jinja_env.get_template('email_progress_update.html')
        html_body = template.render(**template_data)
        
        # Generar versión texto plano
        text_body = self._generate_text_version(template_data, is_first=False)
        
        # Generar asunto
        subject = f"Actualización de tu Proyecto Solar - {action_info['title']}"
        
        return {
            'subject': subject,
            'html': html_body,
            'text': text_body
        }
    
    def _get_action_info(self, action_data: Dict) -> Dict:
        """
        Obtener información detallada de una acción
        
        Args:
            action_data: Datos de la acción
            
        Returns:
            Dict con title, description y next_steps
        """
        action = action_data.get('action', {})
        action_title = action.get('title', 'Acción completada')
        
        # Buscar descripción en el mapeo
        action_desc_data = self.action_descriptions.get(
            action_title,
            self.action_descriptions.get('default', {})
        )
        
        return {
            'title': action_title,
            'description': action_desc_data.get('description', 'Se ha completado una nueva etapa de tu proyecto solar.'),
            'next_steps': action_desc_data.get('next_steps', 'Nuestro equipo se pondrá en contacto contigo pronto.')
        }
    
    def _generate_text_version(self, data: Dict, is_first: bool = False) -> str:
        """
        Generar versión texto plano del email
        
        Args:
            data: Datos del template
            is_first: Si es la primera notificación
            
        Returns:
            Texto plano del email
        """
        if is_first:
            return f"""
¡Hola, {data['client_name']}!

Te damos una calurosa bienvenida a la familia Green House Project. Estamos muy emocionados de acompañarte en tu transición hacia un futuro más sostenible con energía solar.

PAGO DE CUOTA INICIAL RECIBIDO

Hemos recibido exitosamente el pago de tu cuota inicial. Tu proyecto solar está oficialmente en marcha.

Fecha de completación: {data['completion_date']}

ACCESO A TU PORTAL DE CLIENTE

Hemos creado un portal exclusivo para que puedas seguir cada paso de tu proyecto. Para acceder, necesitarás el siguiente ID:

ID del Proyecto: {data['project_id']}

Visita: {data['portal_url']}

INFORMACIÓN DE TU PROYECTO

Proyecto: {data['project_title']}
Dirección: {data['project_address']}

PRÓXIMOS PASOS

{data['next_steps']}

Si tienes alguna pregunta, no dudes en contactarnos.

¡Gracias por confiar en Green House Project!

Equipo Green House Project
Revoluciona el concepto de vivir

© {data['year']} Green House Project. Todos los derechos reservados.
"""
        else:
            return f"""
¡Hola, {data['client_name']}!

Tu proyecto solar sigue avanzando. Te informamos que se ha completado una nueva etapa:

{data['action_title'].upper()}

{data['action_description']}

Fecha de completación: {data['completion_date']}

INFORMACIÓN DE TU PROYECTO

Proyecto: {data['project_title']}
Dirección: {data['project_address']}
ID del Proyecto: {data['project_id']}

PRÓXIMOS PASOS

{data['next_steps']}

Puedes consultar el estado completo de tu proyecto en: {data['portal_url']}

Si tienes alguna pregunta, no dudes en contactarnos.

¡Gracias por confiar en Green House Project!

Equipo Green House Project
Revoluciona el concepto de vivir

© {data['year']} Green House Project. Todos los derechos reservados.
"""
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str) -> bool:
        """
        Enviar email (placeholder - debe ser implementado con servicio real)
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            html_body: Cuerpo HTML del email
            text_body: Cuerpo texto plano del email
            
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        # TODO: Implementar envío real con Gmail API o servicio de email
        logger.info(f"Email simulado enviado a {to_email}: {subject}")
        logger.info(f"HTML length: {len(html_body)}, Text length: {len(text_body)}")
        return True
