"""
Configuración del sistema de notificaciones automáticas
GreenH Project - OpenSolar Integration
"""

import os
from datetime import timedelta

class Config:
    """Configuración base"""
    
    # Flask
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # Base de datos
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///notifications.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenSolar API
    OPENSOLAR_TOKEN = os.getenv('OPENSOLAR_TOKEN', '')
    OPENSOLAR_ORG_ID = os.getenv('OPENSOLAR_ORG_ID', '80856')
    OPENSOLAR_API_BASE = 'https://api.opensolar.com/api'
    
    # Webhook
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'dev-webhook-secret')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:5000/webhook/opensolar')
    
    # Resend API
    RESEND_API_KEY = os.getenv('RESEND_API_KEY', '')
    
    # Gmail SMTP (deprecated - usando Resend)
    GMAIL_SMTP_PASSWORD = os.getenv('GMAIL_SMTP_PASSWORD', '')
    GMAIL_FROM_EMAIL = 'admin@greenhproject.com'
    GMAIL_FROM_NAME = 'Green House Project'
    
    # Notificaciones
    NOTIFICATION_RETRY_ATTEMPTS = 3
    NOTIFICATION_RETRY_DELAY = 2  # segundos
    RECENT_COMPLETION_THRESHOLD = timedelta(hours=24)
    
    # Portal de clientes
    CLIENT_PORTAL_URL = 'https://www.greenhproject.com/gestionproyectos'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'notifications.log')
    
    # Acciones que activan notificaciones
    TRIGGER_ACTIONS = [
        'pago de cuota inicial',
        'pago cuota inicial',
        'anticipo',
        'inicial'
    ]
    
    # Descripciones de acciones
    ACTION_DESCRIPTIONS = {
        'pago de cuota inicial': {
            'title': 'Pago de Cuota Inicial Recibido',
            'description': 'Hemos recibido exitosamente el pago de tu cuota inicial. Tu proyecto solar está oficialmente en marcha.',
            'next_steps': 'Nuestro equipo técnico realizará una visita al sitio para confirmar las especificaciones del diseño.',
            'is_trigger': True
        },
        'visita tecnica': {
            'title': 'Visita Técnica Completada',
            'description': 'Nuestro equipo técnico ha completado la visita a tu propiedad y ha verificado todos los detalles necesarios para la instalación.',
            'next_steps': 'Procederemos con la preparación de los documentos finales y la programación de la instalación.'
        },
        'of aprobada': {
            'title': 'Oferta en Firme Aprobada',
            'description': 'Tu oferta en firme ha sido aprobada. Todos los detalles técnicos y financieros están confirmados.',
            'next_steps': 'Iniciaremos los trámites administrativos y la adquisición de los equipos.'
        },
        'envio de oferta en firme al cliente': {
            'title': 'Oferta en Firme Enviada',
            'description': 'Te hemos enviado la oferta en firme con todos los detalles de tu proyecto solar.',
            'next_steps': 'Por favor revisa la oferta y confirma tu aprobación para continuar con el proceso.'
        },
        'aprobacion de of': {
            'title': 'Aprobación de Oferta en Firme',
            'description': 'Hemos recibido tu aprobación de la oferta en firme.',
            'next_steps': 'Procederemos con los siguientes pasos del proceso de instalación.'
        },
        'radicacion de documentos credito': {
            'title': 'Documentos de Crédito Radicados',
            'description': 'Hemos radicado los documentos necesarios para el proceso de financiación.',
            'next_steps': 'Estaremos pendientes de la respuesta de la entidad financiera.'
        },
        'preaprobado de credito': {
            'title': 'Crédito Preaprobado',
            'description': 'Tu solicitud de crédito ha sido preaprobada.',
            'next_steps': 'Continuaremos con el proceso de aprobación final.'
        },
        'agendar instalacion': {
            'title': 'Instalación Programada',
            'description': 'Hemos programado la fecha de instalación de tu sistema solar.',
            'next_steps': 'Te contactaremos para confirmar la fecha y preparar el sitio para la instalación.'
        },
        'instalacion realizada': {
            'title': 'Instalación Completada',
            'description': '¡Felicitaciones! La instalación de tu sistema solar ha sido completada exitosamente.',
            'next_steps': 'Realizaremos las pruebas finales y la conexión a la red eléctrica.'
        }
    }


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///test_notifications.db'
    SQLALCHEMY_DATABASE_URI = DATABASE_URL


# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtener configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
