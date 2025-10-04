"""
Modelos de base de datos para el sistema de notificaciones
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json


class Database:
    """Clase para manejar la conexión y operaciones de base de datos"""
    
    def __init__(self, db_path: str = 'notifications.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
        return conn
    
    def init_database(self):
        """Inicializar la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de notificaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                project_identifier TEXT,
                project_title TEXT,
                action_id INTEGER NOT NULL,
                action_title TEXT NOT NULL,
                recipient_email TEXT NOT NULL,
                recipient_name TEXT,
                email_type TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                email_subject TEXT,
                email_body TEXT,
                status TEXT DEFAULT 'sent',
                error_message TEXT,
                webhook_data TEXT
            )
        ''')
        
        # Tabla de configuración
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear índices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_project_id 
            ON notifications(project_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_sent_at 
            ON notifications(sent_at)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON notifications(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_action_id 
            ON notifications(action_id)
        ''')
        
        conn.commit()
        conn.close()


class Notification:
    """Modelo para notificaciones"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self

, 
               project_id: int,
               action_id: int,
               action_title: str,
               recipient_email: str,
               email_type: str,
               email_subject: str,
               email_body: str,
               project_identifier: Optional[str] = None,
               project_title: Optional[str] = None,
               recipient_name: Optional[str] = None,
               webhook_data: Optional[Dict] = None,
               status: str = 'sent',
               error_message: Optional[str] = None) -> int:
        """
        Crear una nueva notificación en la base de datos
        
        Returns:
            ID de la notificación creada
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        webhook_json = json.dumps(webhook_data) if webhook_data else None
        
        cursor.execute('''
            INSERT INTO notifications (
                project_id, project_identifier, project_title,
                action_id, action_title, recipient_email, recipient_name,
                email_type, email_subject, email_body,
                status, error_message, webhook_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project_id, project_identifier, project_title,
            action_id, action_title, recipient_email, recipient_name,
            email_type, email_subject, email_body,
            status, error_message, webhook_json
        ))
        
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return notification_id
    
    def get_by_id(self, notification_id: int) -> Optional[Dict]:
        """Obtener notificación por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM notifications WHERE id = ?', (notification_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_by_project(self, project_id: int) -> List[Dict]:
        """Obtener todas las notificaciones de un proyecto"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE project_id = ? 
            ORDER BY sent_at DESC
        ''', (project_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def check_if_notified(self, project_id: int, action_id: int) -> bool:
        """
        Verificar si ya se notificó una acción específica de un proyecto
        
        Returns:
            True si ya se notificó, False si no
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE project_id = ? AND action_id = ? AND status = 'sent'
        ''', (project_id, action_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] > 0
    
    def check_if_first_notification(self, project_id: int) -> bool:
        """
        Verificar si es la primera notificación para un proyecto
        
        Returns:
            True si es la primera, False si ya hay notificaciones previas
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE project_id = ? AND status = 'sent'
        ''', (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result['count'] == 0
    
    def update_status(self, notification_id: int, status: str, error_message: Optional[str] = None):
        """Actualizar el estado de una notificación"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications 
            SET status = ?, error_message = ? 
            WHERE id = ?
        ''', (status, error_message, notification_id))
        
        conn.commit()
        conn.close()
    
    def get_recent_notifications(self, limit: int = 50) -> List[Dict]:
        """Obtener las notificaciones más recientes"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications 
            ORDER BY sent_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_failed_notifications(self) -> List[Dict]:
        """Obtener notificaciones fallidas"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE status = 'failed' 
            ORDER BY sent_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


class ConfigModel:
    """Modelo para configuración"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get(self, key: str) -> Optional[str]:
        """Obtener valor de configuración"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['value']
        return None
    
    def set(self, key: str, value: str):
        """Establecer valor de configuración"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
    
    def get_all(self) -> Dict[str, str]:
        """Obtener toda la configuración"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM config')
        rows = cursor.fetchall()
        conn.close()
        
        return {row['key']: row['value'] for row in rows}
