import sqlite3
import os

db_path = "data/th_platform.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Intentar agregar la columna observaciones a la tabla tasks
        cursor.execute("ALTER TABLE tasks ADD COLUMN observations TEXT")
        conn.commit()
        print("✅ Columna 'observations' añadida con éxito.")
    except sqlite3.OperationalError:
        print("ℹ️ La columna 'observations' ya existe.")
    finally:
        conn.close()
else:
    print("❌ Base de datos no encontrada.")
