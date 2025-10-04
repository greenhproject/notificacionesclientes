#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para el sistema de notificaciones automáticas
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from services import NotificationService, GmailService

# Configuración
config = get_config()

# Inicializar servicios
notification_service = NotificationService(
    templates_dir=os.path.join(os.path.dirname(__file__), "templates"),
    client_portal_url=config.CLIENT_PORTAL_URL,
    action_descriptions=config.ACTION_DESCRIPTIONS
)

gmail_service = GmailService(
    from_email=config.GMAIL_FROM_EMAIL,
    from_name=config.GMAIL_FROM_NAME
)

# Datos de prueba
client_data = {
    'email': 'admin@greenhproject.com',
    'first_name': 'Juan',
    'family_name': 'Pérez',
    'full_name': 'Juan Pérez',
    'phone': '+57 300 1234567'
}

project_data = {
    'id': 12345,
    'identifier': 'GHP-2025-001',
    'title': 'Instalación Solar Residencial',
    'address': 'Calle 123 #45-67, Cali, Valle del Cauca'
}

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
print("PRUEBA DEL SISTEMA DE NOTIFICACIONES AUTOMÁTICAS")
print("GreenH Project - OpenSolar Integration")
print("=" * 80)
print()

# Prueba 1: Generar email de primera notificación
print("1. Generando email de primera notificación (bienvenida)...")
print("-" * 80)

first_email = notification_service.generate_first_notification_email(
    client_data, project_data, action_data
)

print(f"Asunto: {first_email['subject']}")
print(f"Longitud HTML: {len(first_email['html'])} caracteres")
print(f"Longitud Plain: {len(first_email['plain'])} caracteres")
print()

# Guardar HTML para inspección
with open("/home/ubuntu/test_first_notification.html", "w", encoding="utf-8") as f:
    f.write(first_email['html'])
print("✓ HTML guardado en: /home/ubuntu/test_first_notification.html")
print()

# Prueba 2: Enviar email de primera notificación
print("2. Enviando email de primera notificación...")
print("-" * 80)

success = gmail_service.send_email(
    to=client_data['email'],
    subject=first_email['subject'],
    html_body=first_email['html'],
    plain_body=first_email['plain']
)

if success:
    print(f"✓ Email de bienvenida enviado exitosamente a {client_data['email']}")
else:
    print(f"✗ Error al enviar email de bienvenida a {client_data['email']}")
print()

# Prueba 3: Generar email de actualización de progreso
print("3. Generando email de actualización de progreso...")
print("-" * 80)

action_data_progress = {
    'action': {
        'id': 1002,
        'title': 'Visita técnica'
    },
    'event': {
        'is_complete': True,
        'completion_date': datetime.now()
    },
    'completion_date': datetime.now()
}

progress_email = notification_service.generate_progress_update_email(
    client_data, project_data, action_data_progress
)

print(f"Asunto: {progress_email['subject']}")
print(f"Longitud HTML: {len(progress_email['html'])} caracteres")
print(f"Longitud Plain: {len(progress_email['plain'])} caracteres")
print()

# Guardar HTML para inspección
with open("/home/ubuntu/test_progress_update.html", "w", encoding="utf-8") as f:
    f.write(progress_email['html'])
print("✓ HTML guardado en: /home/ubuntu/test_progress_update.html")
print()

# Prueba 4: Enviar email de actualización de progreso
print("4. Enviando email de actualización de progreso...")
print("-" * 80)

success = gmail_service.send_email(
    to=client_data['email'],
    subject=progress_email['subject'],
    html_body=progress_email['html'],
    plain_body=progress_email['plain']
)

if success:
    print(f"✓ Email de actualización enviado exitosamente a {client_data['email']}")
else:
    print(f"✗ Error al enviar email de actualización a {client_data['email']}")
print()

print("=" * 80)
print("PRUEBAS COMPLETADAS")
print("=" * 80)
print()
print("Revisa tu bandeja de entrada en admin@greenhproject.com para ver los emails.")
print("Los archivos HTML generados están disponibles en:")
print("  - /home/ubuntu/test_first_notification.html")
print("  - /home/ubuntu/test_progress_update.html")
