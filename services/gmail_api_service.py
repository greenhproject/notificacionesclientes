"""
Servicio de integración con Gmail usando Gmail API
"""

import os
import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

logger = logging.getLogger(__name__)

# Alcances necesarios para enviar emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


class GmailAPIService:
    """Servicio para enviar emails usando Gmail API"""
    
    def __init__(self, from_email: str, from_name: str = None, 
                 credentials_file: str = 'credentials.json',
                 token_file: str = 'token.pickle'):
        """
        Inicializar servicio de Gmail con API
        
        Args:
            from_email: Email del remitente
            from_name: Nombre del remitente (opcional)
            credentials_file: Ruta al archivo de credenciales OAuth
            token_file: Ruta al archivo de token guardado
        """
        self.from_email = from_email
        self.from_name = from_name or from_email
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autenticar con Gmail API usando OAuth 2.0"""
        creds = None
        
        # Cargar token guardado si existe
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                logger.info("Token de autenticación cargado desde archivo")
            except Exception as e:
                logger.warning(f"Error al cargar token: {e}")
        
        # Si no hay credenciales válidas, obtener nuevas
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refrescando token de autenticación...")
                    creds.refresh(Request())
                    logger.info("Token refrescado exitosamente")
                except Exception as e:
                    logger.error(f"Error al refrescar token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Archivo de credenciales no encontrado: {self.credentials_file}"
                    )
                
                logger.info("Iniciando flujo de autenticación OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=8080)
                logger.info("Autenticación completada")
            
            # Guardar credenciales para futuros usos
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info(f"Token guardado en {self.token_file}")
            except Exception as e:
                logger.warning(f"No se pudo guardar el token: {e}")
        
        # Crear servicio de Gmail API
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("Servicio de Gmail API inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al crear servicio de Gmail API: {e}")
            raise
    
    def send_email(self, to: str, subject: str, html_body: str, 
                   plain_body: Optional[str] = None) -> bool:
        """
        Enviar email usando Gmail API
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            html_body: Cuerpo del email en HTML
            plain_body: Cuerpo del email en texto plano (opcional)
            
        Returns:
            True si se envió exitosamente, False si hubo error
        """
        if not self.service:
            logger.error("Servicio de Gmail API no está inicializado")
            return False
        
        try:
            # Crear mensaje
            message = MIMEMultipart('alternative')
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to
            message['Subject'] = subject
            
            # Agregar cuerpo en texto plano si se proporciona
            if plain_body:
                part1 = MIMEText(plain_body, 'plain', 'utf-8')
                message.attach(part1)
            
            # Agregar cuerpo en HTML
            part2 = MIMEText(html_body, 'html', 'utf-8')
            message.attach(part2)
            
            # Codificar mensaje en base64
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Enviar email
            logger.info(f"Enviando email a {to} con asunto: {subject}")
            send_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"Email enviado exitosamente a {to}. ID: {send_message['id']}")
            return True
                
        except Exception as e:
            logger.error(f"Error al enviar email a {to}: {e}")
            return False
    
    def send_email_with_retry(self, to: str, subject: str, html_body: str,
                             plain_body: Optional[str] = None,
                             max_retries: int = 3) -> bool:
        """
        Enviar email con reintentos en caso de fallo
        
        Args:
            to: Email del destinatario
            subject: Asunto del email
            html_body: Cuerpo del email en HTML
            plain_body: Cuerpo del email en texto plano (opcional)
            max_retries: Número máximo de reintentos
            
        Returns:
            True si se envió exitosamente, False si falló después de todos los reintentos
        """
        import time
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"Intento {attempt} de {max_retries} para enviar email a {to}")
            
            success = self.send_email(to, subject, html_body, plain_body)
            
            if success:
                return True
            
            if attempt < max_retries:
                wait_time = 2 ** attempt  # Backoff exponencial: 2, 4, 8 segundos
                logger.warning(f"Reintentando en {wait_time} segundos...")
                time.sleep(wait_time)
        
        logger.error(f"Falló el envío de email a {to} después de {max_retries} intentos")
        return False
