"""
Servicio de integración con Gmail usando SMTP
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import time

logger = logging.getLogger(__name__)


class GmailService:
    """Servicio para enviar emails usando Gmail SMTP"""
    
    def __init__(self, from_email: str, from_name: str = None, smtp_password: str = None):
        """
        Inicializar servicio de Gmail con SMTP
        
        Args:
            from_email: Email del remitente
            from_name: Nombre del remitente (opcional)
            smtp_password: Contraseña de aplicación de Gmail
        """
        self.from_email = from_email
        self.from_name = from_name or from_email
        self.smtp_password = smtp_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_email(self, to: str, subject: str, html_body: str, 
                   plain_body: Optional[str] = None) -> bool:
        """
        Enviar email usando Gmail SMTP
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            html_body: Cuerpo del email en HTML
            plain_body: Cuerpo del email en texto plano (opcional)
            
        Returns:
            True si se envió exitosamente, False si hubo error
        """
        if not self.smtp_password:
            logger.error("No se ha configurado la contraseña SMTP de Gmail")
            return False
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to
            msg['Subject'] = subject
            
            # Agregar cuerpo en texto plano si se proporciona
            if plain_body:
                part1 = MIMEText(plain_body, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Agregar cuerpo en HTML
            part2 = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(part2)
            
            # Conectar al servidor SMTP de Gmail
            logger.info(f"Conectando a {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            # Autenticar
            logger.info(f"Autenticando como {self.from_email}")
            server.login(self.from_email, self.smtp_password)
            
            # Enviar email
            logger.info(f"Enviando email a {to} con asunto: {subject}")
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email enviado exitosamente a {to}")
            return True
                
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Error de autenticación SMTP: {e}")
            logger.error("Verifica que la contraseña de aplicación de Gmail sea correcta")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP al enviar email a {to}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado al enviar email a {to}: {e}")
            return False
    
    def send_email_with_retry(self, to: str, subject: str, html_body: str,
                             plain_body: Optional[str] = None,
                             max_retries: int = 3) -> bool:
        """
        Enviar email con reintentos en caso de error
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            html_body: Cuerpo del email en HTML
            plain_body: Cuerpo del email en texto plano (opcional)
            max_retries: Número máximo de reintentos
            
        Returns:
            True si se envió exitosamente, False si falló después de todos los reintentos
        """
        for attempt in range(max_retries):
            try:
                success = self.send_email(to, subject, html_body, plain_body)
                
                if success:
                    return True
                
                # Si no fue exitoso y no es el último intento, esperar antes de reintentar
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Backoff exponencial
                    logger.info(f"Reintentando envío en {wait_time} segundos...")
                    time.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Intento {attempt + 1} fallido: {e}")
                
                if attempt == max_retries - 1:
                    logger.error(f"Todos los intentos fallaron para enviar email a {to}")
                    return False
                
                # Esperar antes de reintentar
                wait_time = 2 ** attempt
                time.sleep(wait_time)
        
        return False
    
    def test_connection(self) -> bool:
        """
        Probar la conexión SMTP y autenticación
        
        Returns:
            True si la conexión es exitosa, False en caso contrario
        """
        if not self.smtp_password:
            logger.error("No se ha configurado la contraseña SMTP de Gmail")
            return False
        
        try:
            logger.info(f"Probando conexión a {self.smtp_server}:{self.smtp_port}")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            logger.info(f"Probando autenticación como {self.from_email}")
            server.login(self.from_email, self.smtp_password)
            server.quit()
            
            logger.info("Conexión y autenticación exitosas")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Error de autenticación: {e}")
            return False
        except Exception as e:
            logger.error(f"Error al probar conexión: {e}")
            return False
