import os
import psycopg2
from urllib.parse import urlparse

# Leer la URL de la base de datos que Railway inyecta automáticamente
DATABASE_URL = os.environ.get("DATABASE_URL")

def obtener_conexion():
    """Crea una conexión segura con la base de datos PostgreSQL en Railway."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def inicializar_base_datos():
    """Crea la tabla de memoria si no existe."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Ejecutar esto al arrancar tu servidor
inicializar_base_datos()

def guardar_mensaje(session_id, role, message):
    """Guarda un mensaje en la base de datos de la nube."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (session_id, role, message) VALUES (%s, %s, %s)",
            (session_id, role, message)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error guardando en BD: {e}")

def obtener_historial(session_id, limite=10):
    """Recupera los últimos mensajes de la sesión para darle contexto a la IA."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, message FROM chat_history WHERE session_id = %s ORDER BY created_at DESC LIMIT %s",
            (session_id, limite)
        )
        filas = cursor.fetchall()
        cursor.close()
        conn.close()
        # Invertir para que queden en orden cronológico
        return [{"role": r[0], "content": r[1]} for r in reversed(filas)]
    except Exception as e:
        print(f"Error leyendo BD: {e}")
        return []
