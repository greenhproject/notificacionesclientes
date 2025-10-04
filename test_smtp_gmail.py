#!/usr/bin/env python3
"""
Script para probar el envío de correos usando Gmail SMTP
"""

import os
import sys
from services.gmail_service import GmailService

def test_gmail_smtp():
    """Probar el servicio de Gmail SMTP"""
    
    # Obtener credenciales
    from_email = "admin@greenhproject.com"
    from_name = "Green House Project"
    smtp_password = os.getenv("GMAIL_SMTP_PASSWORD", "")
    
    if not smtp_password:
        print("❌ Error: No se ha configurado GMAIL_SMTP_PASSWORD")
        print("Configura la variable de entorno: export GMAIL_SMTP_PASSWORD='tu-contraseña-de-aplicacion'")
        return False
    
    print(f"📧 Probando servicio de Gmail SMTP")
    print(f"   Remitente: {from_name} <{from_email}>")
    print()
    
    # Crear servicio
    gmail_service = GmailService(
        from_email=from_email,
        from_name=from_name,
        smtp_password=smtp_password
    )
    
    # Probar conexión
    print("🔌 Probando conexión y autenticación...")
    if not gmail_service.test_connection():
        print("❌ Error: No se pudo conectar o autenticar con Gmail SMTP")
        return False
    
    print("✅ Conexión y autenticación exitosas")
    print()
    
    # Solicitar email de prueba
    test_email = input("Ingresa el email de destino para la prueba: ").strip()
    
    if not test_email or "@" not in test_email:
        print("❌ Email inválido")
        return False
    
    # Crear email de prueba
    subject = "Prueba de Sistema de Notificaciones - Green House Project"
    html_body = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌞 Green House Project</h1>
                <p>Sistema de Notificaciones Automáticas</p>
            </div>
            <div class="content">
                <h2>¡Prueba Exitosa!</h2>
                <p>Este es un correo de prueba del sistema de notificaciones automáticas de Green House Project.</p>
                <p>Si recibes este mensaje, significa que el sistema está configurado correctamente y listo para enviar notificaciones a tus clientes.</p>
                <p><strong>Características del sistema:</strong></p>
                <ul>
                    <li>✅ Integración con OpenSolar</li>
                    <li>✅ Notificaciones automáticas por cambios de estado</li>
                    <li>✅ Diseño profesional y responsive</li>
                    <li>✅ Envío confiable mediante Gmail SMTP</li>
                </ul>
            </div>
            <div class="footer">
                <p>Green House Project | Sistema de Notificaciones Automáticas</p>
                <p>Este es un correo automático, por favor no responder.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_body = """
    Green House Project - Sistema de Notificaciones Automáticas
    
    ¡Prueba Exitosa!
    
    Este es un correo de prueba del sistema de notificaciones automáticas de Green House Project.
    Si recibes este mensaje, significa que el sistema está configurado correctamente.
    """
    
    # Enviar email
    print(f"📤 Enviando email de prueba a {test_email}...")
    success = gmail_service.send_email(
        to=test_email,
        subject=subject,
        html_body=html_body,
        plain_body=plain_body
    )
    
    if success:
        print("✅ Email enviado exitosamente")
        print(f"   Revisa la bandeja de entrada de {test_email}")
        return True
    else:
        print("❌ Error al enviar email")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("  Prueba de Gmail SMTP - Green House Project")
    print("=" * 60)
    print()
    
    success = test_gmail_smtp()
    
    print()
    print("=" * 60)
    if success:
        print("✅ Prueba completada exitosamente")
    else:
        print("❌ Prueba fallida")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
