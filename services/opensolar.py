"""
Servicio de integración con OpenSolar API
"""

import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OpenSolarService:
    """Servicio para interactuar con la API de OpenSolar"""
    
    def __init__(self, api_token: str, org_id: str, base_url: str = 'https://api.opensolar.com/api'):
        self.api_token = api_token
        self.org_id = org_id
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """
        Obtener información completa de un proyecto
        
        Args:
            project_id: ID del proyecto en OpenSolar
            
        Returns:
            Diccionario con datos del proyecto o None si hay error
        """
        url = f"{self.base_url}/orgs/{self.org_id}/projects/{project_id}/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener proyecto {project_id}: {e}")
            return None
    
    def get_recently_completed_actions(self, actions: List[Dict], 
                                      threshold_hours: int = 24) -> List[Dict]:
        """
        Obtener acciones que se completaron recientemente
        
        Args:
            actions: Lista de acciones del proyecto
            threshold_hours: Número de horas hacia atrás para considerar "reciente"
            
        Returns:
            Lista de acciones completadas recientemente con sus eventos
        """
        recently_completed = []
        now = datetime.utcnow()
        threshold = now - timedelta(hours=threshold_hours)
        
        for action in actions:
            events = action.get('events', [])
            
            if not events:
                continue
            
            # Buscar el evento más reciente que esté completado
            for event in events:
                if not event.get('is_complete'):
                    continue
                
                completion_date_str = event.get('completion_date')
                if not completion_date_str:
                    continue
                
                try:
                    # Parsear fecha de completación
                    # Formato: "2025-09-10 13:34:43.759047+00:00" o "2025-09-10T13:34:43.759047Z"
                    completion_date_str = completion_date_str.replace(' ', 'T').replace('Z', '+00:00')
                    completion_date = datetime.fromisoformat(completion_date_str)
                    
                    # Hacer timezone-naive para comparación
                    if completion_date.tzinfo:
                        completion_date = completion_date.replace(tzinfo=None)
                    
                    # Si se completó recientemente
                    if completion_date >= threshold:
                        recently_completed.append({
                            'action': action,
                            'event': event,
                            'completion_date': completion_date
                        })
                        break  # Solo el evento más reciente por acción
                
                except (ValueError, AttributeError) as e:
                    logger.warning(f"Error al parsear fecha de completación: {e}")
                    continue
        
        return recently_completed
    
    def is_initial_payment_action(self, action: Dict, trigger_keywords: List[str]) -> bool:
        """
        Verificar si una acción es el pago de cuota inicial
        
        Args:
            action: Diccionario con datos de la acción
            trigger_keywords: Lista de palabras clave que identifican el pago inicial
            
        Returns:
            True si es el pago inicial, False si no
        """
        action_title = action.get('title', '').lower().strip()
        
        return any(keyword.lower() in action_title for keyword in trigger_keywords)
    
    def get_action_description(self, action_title: str, descriptions_map: Dict) -> Dict:
        """
        Obtener descripción de una acción basada en su título
        
        Args:
            action_title: Título de la acción
            descriptions_map: Mapeo de títulos a descripciones
            
        Returns:
            Diccionario con título, descripción y próximos pasos
        """
        action_key = action_title.lower().strip()
        
        # Buscar coincidencia exacta o parcial
        for key, info in descriptions_map.items():
            if key in action_key or action_key in key:
                return info
        
        # Descripción genérica si no se encuentra
        return {
            'title': f'Actualización: {action_title}',
            'description': f'Se ha completado la acción "{action_title}" en tu proyecto solar.',
            'next_steps': 'Nuestro equipo continuará trabajando en las siguientes etapas del proyecto.'
        }
    
    def extract_client_data(self, project: Dict) -> Optional[Dict]:
        """
        Extraer datos del cliente principal del proyecto
        
        Args:
            project: Diccionario con datos del proyecto
            
        Returns:
            Diccionario con datos del cliente o None si no hay contactos
        """
        contacts_data = project.get('contacts_data', [])
        
        if not contacts_data:
            logger.warning(f"Proyecto {project.get('id')} no tiene contactos")
            return None
        
        # Tomar el primer contacto como cliente principal
        client = contacts_data[0]
        
        return {
            'email': client.get('email', ''),
            'first_name': client.get('first_name', ''),
            'family_name': client.get('family_name', ''),
            'full_name': f"{client.get('first_name', '')} {client.get('family_name', '')}".strip(),
            'phone': client.get('phone', ''),
            'display': client.get('display', '')
        }
    
    def create_webhook(self, endpoint_url: str, webhook_secret: str, 
                      trigger_fields: List[str], payload_fields: List[str]) -> Optional[Dict]:
        """
        Crear un webhook en OpenSolar
        
        Args:
            endpoint_url: URL del endpoint que recibirá los webhooks
            webhook_secret: Token secreto para autenticación
            trigger_fields: Campos que dispararán el webhook
            payload_fields: Campos que se incluirán en el payload
            
        Returns:
            Diccionario con datos del webhook creado o None si hay error
        """
        url = f"{self.base_url}/orgs/{self.org_id}/webhooks/"
        
        payload = {
            'endpoint': endpoint_url,
            'headers': f'{{"Authorization": "Bearer {webhook_secret}"}}',
            'enabled': True,
            'debug': False,
            'trigger_fields': trigger_fields,
            'payload_fields': payload_fields
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            webhook_data = response.json()
            logger.info(f"Webhook creado exitosamente: {webhook_data.get('id')}")
            return webhook_data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al crear webhook: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Respuesta: {e.response.text}")
            return None
    
    def get_webhooks(self) -> List[Dict]:
        """
        Obtener lista de webhooks configurados
        
        Returns:
            Lista de webhooks
        """
        url = f"{self.base_url}/orgs/{self.org_id}/webhooks/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener webhooks: {e}")
            return []
    
    def update_webhook(self, webhook_id: int, enabled: Optional[bool] = None,
                      trigger_fields: Optional[List[str]] = None,
                      payload_fields: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Actualizar configuración de un webhook
        
        Args:
            webhook_id: ID del webhook a actualizar
            enabled: Si el webhook está habilitado
            trigger_fields: Nuevos campos de trigger (opcional)
            payload_fields: Nuevos campos de payload (opcional)
            
        Returns:
            Diccionario con datos del webhook actualizado o None si hay error
        """
        url = f"{self.base_url}/orgs/{self.org_id}/webhooks/{webhook_id}/"
        
        payload = {}
        if enabled is not None:
            payload['enabled'] = enabled
        if trigger_fields is not None:
            payload['trigger_fields'] = trigger_fields
        if payload_fields is not None:
            payload['payload_fields'] = payload_fields
        
        try:
            response = requests.patch(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al actualizar webhook {webhook_id}: {e}")
            return None
