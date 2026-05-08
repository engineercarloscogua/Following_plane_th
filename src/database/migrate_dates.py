import sqlite3
import os

db_path = "data/th_platform.sqlite"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Añadir start_date y end_date
        cursor.execute("ALTER TABLE tasks ADD COLUMN start_date DATETIME")
        cursor.execute("ALTER TABLE tasks ADD COLUMN end_date DATETIME")
        
        # Migrar target_date a end_date si existe datos
        cursor.execute("UPDATE tasks SET end_date = target_date WHERE target_date IS NOT NULL")
        
        conn.commit()
        print("✅ Columnas de fechas (inicio/fin) añadidas con éxito.")
    except sqlite3.OperationalError as e:
        print(f"ℹ️ Nota: {e}")
    finally:
        conn.close()
else:
    print("❌ Base de datos no encontrada.")
