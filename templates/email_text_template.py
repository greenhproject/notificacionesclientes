"""
Plantillas de correo en texto plano con formato estético
"""

def generate_first_notification_text(client_data, project_data, action_info):
    """Generar correo de primera notificación en texto plano estético"""
    
    project_name = project_data.get('title', 'Tu Proyecto Solar')
    project_id = project_data.get('id', '')
    location = project_data.get('title', '')
    action_title = action_info['action'].get('title', 'Acción completada')
    completion_date = action_info.get('completion_date_formatted', '')
    
    text = f"""
🌱 GREEN HOUSE PROJECT 🌱


¡BIENVENIDO A GREEN HOUSE PROJECT!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


¡Hola{', ' + client_data.get('first_name', '') if client_data.get('first_name') else ''}!

Te damos una calurosa bienvenida a la familia Green House Project. 
Estamos muy emocionados de acompañarte en tu transición hacia un 
futuro más sostenible y eficiente energéticamente.


📋 ACCESO A TU PORTAL DE CLIENTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hemos creado un portal exclusivo donde podrás:

  ✓ Ver el progreso de tu instalación en tiempo real
  ✓ Acceder a toda la documentación de tu proyecto
  ✓ Revisar el cronograma de trabajo
  ✓ Comunicarte directamente con nuestro equipo

🔗 Accede aquí: https://www.greenhproject.com/gestionproyectos


✅ PRIMERA ETAPA COMPLETADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📌 Acción: {action_title}
  📅 Fecha: {completion_date}


📊 RESUMEN DE TU PROYECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Proyecto:  {project_name}
  ID:        {project_id}
  Ubicación: {location}


📞 ¿NECESITAS AYUDA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estamos aquí para ayudarte en cada paso del camino.

  📧 Email: admin@greenhproject.com
  🌐 Web: https://www.greenhproject.com


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este es un mensaje automático del sistema de notificaciones 
de Green House Project.

© 2025 Green House Project. Todos los derechos reservados.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return text.strip()


def generate_progress_update_text(client_data, project_data, action_info):
    """Generar correo de actualización de progreso en texto plano estético"""
    
    project_name = project_data.get('title', 'Tu Proyecto Solar')
    project_id = project_data.get('id', '')
    location = project_data.get('title', '')
    action_title = action_info['action'].get('title', 'Acción completada')
    completion_date = action_info.get('completion_date_formatted', '')
    
    text = f"""
🌱 GREEN HOUSE PROJECT 🌱


NUEVO AVANCE EN TU PROYECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


¡Hola{', ' + client_data.get('first_name', '') if client_data.get('first_name') else ''}!

Queremos mantenerte informado sobre cada avance en tu proyecto solar.
Hemos completado una nueva etapa:


✅ ETAPA COMPLETADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  📌 Acción: {action_title}
  📅 Fecha: {completion_date}

Se ha completado una nueva etapa de tu proyecto solar.


🔄 PRÓXIMOS PASOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nuestro equipo se pondrá en contacto contigo pronto para 
coordinar los siguientes pasos.


📊 RESUMEN DE TU PROYECTO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Proyecto:  {project_name}
  ID:        {project_id}
  Ubicación: {location}


🔗 VER PROGRESO COMPLETO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Puedes ver todos los detalles y el progreso completo de tu 
instalación en tu portal de cliente:

👉 https://www.greenhproject.com/gestionproyectos


📞 ¿NECESITAS AYUDA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Estamos aquí para ayudarte en cada paso del camino.

  📧 Email: admin@greenhproject.com
  🌐 Web: https://www.greenhproject.com


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este es un mensaje automático del sistema de notificaciones 
de Green House Project.

© 2025 Green House Project. Todos los derechos reservados.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    return text.strip()
