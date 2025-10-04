#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba con datos reales de OpenSolar
Simula el envío de notificación a un cliente real
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from services import NotificationService

# Configuración
config = get_config()

# Inicializar servicios
notification_service = NotificationService(
    templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
    client_portal_url=config.CLIENT_PORTAL_URL,
    action_descriptions=config.ACTION_DESCRIPTIONS
)

# Datos reales del proyecto de OpenSolar
client_data = {
    'email': 'admin@greenhproject.com',  # Email de prueba (cambiar por el real si deseas)
    'first_name': 'Carlos Eduardo',
    'family_name': 'Ordoñez Arias',
    'full_name': 'Carlos Eduardo Ordoñez Arias',
    'phone': '(57)313 4019891'
}

project_data = {
    'id': 7772938,
    'identifier': 'GHP-7772938',
    'title': 'Instalación Solar Residencial',
    'address': 'Km 3 Vía Chipaya Parcelación Campestre Valle Verde Casa 72A J, Jamundi'
}

# Simular que se completó el pago de cuota inicial
action_data = {
    'action': {
        'id': 1001,
        'title': 'Pago de cuota inicial'
    },
    'event': {
        'is_complete': True,
        'completion_date': datetime.now()
    },
    'completion_date': datetime.now()
}

print("=" * 80)
print("PRUEBA CON DATOS REALES DE OPENSOLAR")
print("Green House Project - Sistema de Notificaciones Automáticas")
print("=" * 80)
print()
print("DATOS DEL CLIENTE (OpenSolar):")
print(f"  Nombre: {client_data['full_name']}")
print(f"  Email: {client_data['email']}")
print(f"  Teléfono: {client_data['phone']}")
print()
print("DATOS DEL PROYECTO (OpenSolar):")
print(f"  ID: {project_data['id']}")
print(f"  Identificador: {project_data['identifier']}")
print(f"  Título: {project_data['title']}")
print(f"  Dirección: {project_data['address']}")
print()
print("ACCIÓN COMPLETADA:")
print(f"  Título: {action_data['action']['title']}")
print(f"  Fecha: {action_data['completion_date'].strftime('%d de %B de %Y')}")
print()
print("-" * 80)
print()

# Generar email de primera notificación
print("Generando email de bienvenida con datos reales...")
first_email = notification_service.generate_first_notification_email(
    client_data, project_data, action_data
)

print(f"✓ Email generado exitosamente")
print(f"  Asunto: {first_email['subject']}")
print(f"  Longitud HTML: {len(first_email['html'])} caracteres")
print()

# Guardar HTML para inspección
html_file = "/home/ubuntu/email_real_client.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(first_email['html'])
print(f"✓ HTML guardado en: {html_file}")
print()

print("=" * 80)
print("EMAIL LISTO PARA ENVIAR")
print("=" * 80)
print()
print("El email ha sido generado con datos reales de OpenSolar.")
print("Para enviarlo, usa la función de Gmail integrada.")
print()
print(f"Destinatario: {client_data['email']}")
print(f"Asunto: {first_email['subject']}")
print()
print("Contenido del email:")
print("- Saludo personalizado: ¡Hola, Carlos Eduardo!")
print("- Confirmación de pago de cuota inicial")
print("- Credenciales de acceso al portal")
print("- ID del proyecto: GHP-7772938")
print("- Dirección del proyecto")
print("- Próximos pasos")
print()
print(f"Archivo HTML disponible en: {html_file}")
