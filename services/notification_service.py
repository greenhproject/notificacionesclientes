"""
Servicio de lógica de notificaciones
"""

import logging
from typing import Dict, List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
    
    def generate_first_notification_email(self, client_data: Dict, 
                                         project_data: Dict,
                                         action_data: Dict) -> Dict:
        """
        Generar email de primera notificación (pago de cuota inicial)
        
        Args:
            client_data: Datos del cliente
            project_data: Datos del proyecto
            action_data: Datos de la acción completada
            
        Returns:
            Diccionario con subject, html_body y plain_body
        """
        # Obtener descripción de la acción
        action_info = self._get_action_info(action_data['action']['title'])
        
        # Datos para el template
        # Obtener solo el número del ID (sin prefijo GHP-)
        project_id_raw = project_data.get('identifier', str(project_data.get('id')))
        project_id = project_id_raw.replace('GHP-', '').replace('ghp-', '') if isinstance(project_id_raw, str) else str(project_data.get('id'))
        
        template_data = {
            'client_name': client_data.get('first_name', client_data.get('full_name', 'Cliente')),
            'project_id': project_id,
            'project_title': project_data.get('title', 'Tu Proyecto Solar'),
            'project_address': project_data.get('address', ''),
            'action_title': action_info['title'],
            'action_description': action_info['description'],
            'next_steps': action_info['next_steps'],
            'portal_url': self.client_portal_url,
            'completion_date': action_data.get('completion_date', '').strftime('%d de %B de %Y') if action_data.get('completion_date') else '',
            'year': '2025'
        }
        
        # Renderizar template HTML
        template = self.jinja_env.get_template('email_first_notification.html')
        html_body = template.render(**template_data)
        
        # Generar versión en texto plano
        plain_body = self._generate_plain_text_first_notification(template_data)
        
        # Asunto
        subject = f"¡Bienvenido a Green House Project! - Acceso a tu Portal de Cliente"
        
        return {
            'subject': subject,
            'html': html_body,
            'plain': plain_body
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
            Diccionario con subject, html_body y plain_body
        """
        # Obtener descripción de la acción
        action_info = self._get_action_info(action_data['action']['title'])
        
        # Datos para el template
        # Obtener solo el número del ID (sin prefijo GHP-)
        project_id_raw = project_data.get('identifier', str(project_data.get('id')))
        project_id = project_id_raw.replace('GHP-', '').replace('ghp-', '') if isinstance(project_id_raw, str) else str(project_data.get('id'))
        
        template_data = {
            'client_name': client_data.get('first_name', client_data.get('full_name', 'Cliente')),
            'project_id': project_id,
            'project_title': project_data.get('title', 'Tu Proyecto Solar'),
            'project_address': project_data.get('address', ''),
            'action_title': action_info['title'],
            'action_description': action_info['description'],
            'next_steps': action_info['next_steps'],
            'portal_url': self.client_portal_url,
            'completion_date': action_data.get('completion_date', '').strftime('%d de %B de %Y') if action_data.get('completion_date') else '',
            'year': '2025'
        }
        
        # Renderizar template HTML
        template = self.jinja_env.get_template('email_progress_update.html')
        html_body = template.render(**template_data)
        
        # Generar versión en texto plano
        plain_body = self._generate_plain_text_progress_update(template_data)
        
        # Asunto
        subject = f"Actualización de tu Proyecto Solar - {action_info['title']}"
        
        return {
            'subject': subject,
            'html': html_body,
            'plain': plain_body
        }
    
    def _get_action_info(self, action_title: str) -> Dict:
        """Obtener información de una acción"""
        action_key = action_title.lower().strip()
        
        # Buscar coincidencia
        for key, info in self.action_descriptions.items():
            if key in action_key or action_key in key:
                return info
        
        # Descripción genérica
        return {
            'title': f'Actualización: {action_title}',
            'description': f'Se ha completado la acción "{action_title}" en tu proyecto solar.',
            'next_steps': 'Nuestro equipo continuará trabajando en las siguientes etapas del proyecto.'
        }
    
    def _generate_plain_text_first_notification(self, data: Dict) -> str:
        """Generar versión en texto plano del email de primera notificación"""
        return f"""
¡Hola {data['client_name']}!

{data['action_title']}

{data['action_description']}

ACCESO A TU PORTAL DE CLIENTE

Ahora puedes consultar el estado de tu proyecto en cualquier momento desde nuestro portal de clientes:

URL: {data['portal_url']}
ID de tu proyecto: {data['project_id']}

Cómo acceder:
1. Ingresa a {data['portal_url']}
2. Introduce el ID de tu proyecto: {data['project_id']}
3. Consulta el estado y detalles de tu instalación solar

PRÓXIMOS PASOS

{data['next_steps']}

INFORMACIÓN DE TU PROYECTO

Proyecto: {data['project_title']}
Dirección: {data['project_address']}
ID: {data['project_id']}

¿Tienes preguntas? Estamos aquí para ayudarte. Responde a este email o contáctanos directamente.

Saludos cordiales,
Equipo Green House Project

---
Este es un mensaje automático del sistema de notificaciones de Green House Project.
© {data['year']} Green House Project. Todos los derechos reservados.
        """.strip()
    
    def _generate_plain_text_progress_update(self, data: Dict) -> str:
        """Generar versión en texto plano del email de actualización de progreso"""
        return f"""
¡Hola {data['client_name']}!

{data['action_title']}

{data['action_description']}

PRÓXIMOS PASOS

{data['next_steps']}

CONSULTA MÁS DETALLES

Puedes ver información completa de tu proyecto en nuestro portal de clientes:
{data['portal_url']}

INFORMACIÓN DE TU PROYECTO

Proyecto: {data['project_title']}
Dirección: {data['project_address']}
ID: {data['project_id']}

¿Tienes preguntas? Estamos aquí para ayudarte. Responde a este email o contáctanos directamente.

Saludos cordiales,
Equipo Green House Project

---
Este es un mensaje automático del sistema de notificaciones de Green House Project.
© {data['year']} Green House Project. Todos los derechos reservados.
        """.strip()
