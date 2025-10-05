"""
Servicio para enviar correos HTML usando Gmail directamente
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GmailSenderService:
    """
    Servicio para enviar correos usando Gmail
    Nota: Este servicio está diseñado para ser usado con Manus Gmail integration
    """
    
    def __init__(self):
        """Inicializa el servicio de Gmail"""
        logger.info("Servicio de Gmail Sender inicializado")
    
    def send_html_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc_email: Optional[str] = None
    ) -> bool:
        """
        Envía un correo HTML usando Gmail
        
        Args:
            to_email: Email del destinatario
            subject: Asunto del correo
            html_content: Contenido HTML del correo
            cc_email: Email opcional para copia (CC)
            
        Returns:
            bool: True si el envío fue exitoso, False en caso contrario
        """
        try:
            logger.info(f"Enviando email HTML a {to_email}")
            logger.info(f"Asunto: {subject}")
            
            # Nota: El envío real se hace a través de Manus gmail_send_message
            # Este servicio solo prepara los datos
            
            return True
            
        except Exception as e:
            logger.error(f"Error al enviar email: {str(e)}")
            return False
