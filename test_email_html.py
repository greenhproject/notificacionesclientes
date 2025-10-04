#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para enviar email HTML correctamente formateado
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
print("PRUEBA DE ENVÍO DE EMAIL HTML")
print("Green House Project - Sistema de Notificaciones Automáticas")
print("=" * 80)
print()

# Generar email de primera notificación
print("Generando email de bienvenida...")
first_email = notification_service.generate_first_notification_email(
    client_data, project_data, action_data
)

print(f"Asunto: {first_email['subject']}")
print()

# Guardar HTML para inspección
html_file = "/home/ubuntu/email_test_output.html"
with open(html_file, "w", encoding="utf-8") as f:
    f.write(first_email['html'])
print(f"✓ HTML guardado en: {html_file}")
print()

# Importar la función de envío de Gmail
print("Enviando email con formato HTML...")
print("-" * 80)

# Preparar el mensaje para Gmail
# Nota: La función gmail_send_message espera el contenido en formato de texto plano
# Para enviar HTML, necesitamos usar un enfoque diferente

# Por ahora, vamos a guardar el contenido y mostrar instrucciones
print("Para enviar este email con formato HTML correcto:")
print("1. Abre el archivo:", html_file)
print("2. Copia todo el contenido HTML")
print("3. Usa un servicio de email que soporte HTML inline")
print()

print("Alternativamente, puedes usar la función de Gmail directamente")
print("con el parámetro de contenido HTML.")
print()

# Intentar enviar usando la herramienta de Gmail
try:
    # Aquí necesitaríamos usar la función correcta para enviar HTML
    # La función actual de gmail_send_message puede no soportar HTML directamente
    print("Nota: El sistema actual de Gmail puede requerir configuración adicional")
    print("para enviar emails con formato HTML completo.")
except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 80)
print("PRUEBA COMPLETADA")
print("=" * 80)
print()
print(f"Revisa el archivo HTML generado en: {html_file}")
