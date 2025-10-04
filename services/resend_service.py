"""
Servicio para enviar correos usando Resend API
"""
import os
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)


class ResendService:
    """Servicio para enviar correos electrónicos usando Resend API"""
    
    def __init__(self, api_key: str):
        """
        Inicializa el servicio de Resend
        
        Args:
            api_key: API key de Resend
        """
        self.api_key = api_key
        self.api_url = "https://api.resend.com/emails"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        logger.info("Servicio de Resend inicializado correctamente")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = "onboarding@resend.dev"
    ) -> bool:
        """
        Envía un correo electrónico usando Resend API
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            from_email: Email del remitente (por defecto usa el dominio de Resend)
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        try:
            logger.info(f"Enviando email a {to_email} con asunto: {subject}")
            
            payload = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Email enviado exitosamente a {to_email}")
                logger.info(f"Respuesta de Resend: {response.json()}")
                return True
            else:
                logger.error(f"Error al enviar email: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al enviar email a {to_email}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al enviar email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar email: {str(e)}")
            return False
    
    def send_email_with_retry(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = "onboarding@resend.dev",
        max_retries: int = 3
    ) -> bool:
        """
        Envía un correo con reintentos en caso de fallo
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            from_email: Email del remitente
            max_retries: Número máximo de reintentos
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"Intento {attempt + 1} de {max_retries} para enviar email a {to_email}")
                
                if self.send_email(to_email, subject, html_content, from_email):
                    return True
                    
                if attempt < max_retries - 1:
                    logger.warning(f"Reintentando envío de email (intento {attempt + 2}/{max_retries})")
                    
            except Exception as e:
                logger.error(f"Error en intento {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.warning(f"Reintentando...")
        
        logger.error(f"No se pudo enviar el email a {to_email} después de {max_retries} intentos")
        return False
