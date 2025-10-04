#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar el webhook en OpenSolar
"""

import os
import sys
import json

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from services import OpenSolarService

def main():
    """Configurar webhook en OpenSolar"""
    
    print("=" * 80)
    print("CONFIGURACIÓN DE WEBHOOK EN OPENSOLAR")
    print("GreenH Project - Sistema de Notificaciones Automáticas")
    print("=" * 80)
    print()
    
    # Cargar configuración
    config = get_config()
    
    # Verificar que las variables de entorno estén configuradas
    if not config.OPENSOLAR_TOKEN:
        print("✗ Error: OPENSOLAR_TOKEN no está configurado")
        print("  Por favor configura la variable de entorno OPENSOLAR_TOKEN")
        sys.exit(1)
    
    if not config.WEBHOOK_SECRET:
        print("✗ Error: WEBHOOK_SECRET no está configurado")
        print("  Por favor configura la variable de entorno WEBHOOK_SECRET")
        sys.exit(1)
    
    if not config.WEBHOOK_URL or config.WEBHOOK_URL == 'http://localhost:5000/webhook/opensolar':
        print("⚠ Advertencia: WEBHOOK_URL no está configurado o usa localhost")
        print(f"  URL actual: {config.WEBHOOK_URL}")
        response = input("¿Deseas continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            sys.exit(0)
    
    print(f"Organización ID: {config.OPENSOLAR_ORG_ID}")
    print(f"Webhook URL: {config.WEBHOOK_URL}")
    print()
    
    # Inicializar servicio de OpenSolar
    opensolar = OpenSolarService(
        api_token=config.OPENSOLAR_TOKEN,
        org_id=config.OPENSOLAR_ORG_ID
    )
    
    # Verificar webhooks existentes
    print("1. Verificando webhooks existentes...")
    print("-" * 80)
    
    existing_webhooks = opensolar.get_webhooks()
    
    if existing_webhooks:
        print(f"Se encontraron {len(existing_webhooks)} webhook(s) existente(s):")
        for i, webhook in enumerate(existing_webhooks, 1):
            print(f"\n  {i}. ID: {webhook.get('id')}")
            print(f"     Endpoint: {webhook.get('endpoint')}")
            print(f"     Habilitado: {webhook.get('enabled')}")
            print(f"     Trigger fields: {webhook.get('trigger_fields')}")
        print()
        
        response = input("¿Deseas crear un nuevo webhook de todos modos? (s/n): ")
        if response.lower() != 's':
            print("\nOperación cancelada.")
            sys.exit(0)
    else:
        print("No se encontraron webhooks existentes.")
    
    print()
    
    # Configurar webhook
    print("2. Creando nuevo webhook...")
    print("-" * 80)
    
    trigger_fields = ["project.actions"]
    payload_fields = [
        "project.id",
        "project.identifier",
        "project.title",
        "project.address",
        "project.contacts_data.*",
        "project.actions",
        "project.stage"
    ]
    
    webhook_data = opensolar.create_webhook(
        endpoint_url=config.WEBHOOK_URL,
        webhook_secret=config.WEBHOOK_SECRET,
        trigger_fields=trigger_fields,
        payload_fields=payload_fields
    )
    
    if webhook_data:
        print("\n✓ Webhook creado exitosamente!")
        print(f"\nDetalles del webhook:")
        print(f"  ID: {webhook_data.get('id')}")
        print(f"  Endpoint: {webhook_data.get('endpoint')}")
        print(f"  Habilitado: {webhook_data.get('enabled')}")
        print(f"  Trigger fields: {webhook_data.get('trigger_fields')}")
        print(f"  Payload fields: {len(webhook_data.get('payload_fields', []))} campos")
        
        # Guardar configuración del webhook
        webhook_config_file = "webhook_config.json"
        with open(webhook_config_file, "w") as f:
            json.dump(webhook_data, f, indent=2)
        
        print(f"\n✓ Configuración guardada en: {webhook_config_file}")
    else:
        print("\n✗ Error al crear el webhook")
        print("  Revisa los logs para más detalles")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("CONFIGURACIÓN COMPLETADA")
    print("=" * 80)
    print()
    print("El webhook está configurado y listo para recibir notificaciones de OpenSolar.")
    print(f"Asegúrate de que tu aplicación esté desplegada y accesible en: {config.WEBHOOK_URL}")


if __name__ == "__main__":
    main()
