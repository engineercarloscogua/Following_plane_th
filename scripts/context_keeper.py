#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import sqlite3
from datetime import datetime

# Define paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTEXT_FILE = os.path.join(ROOT_DIR, "PROJECT_CONTEXT.md")
DB_PATH = os.path.join(ROOT_DIR, "data", "th_platform.sqlite")

def run_cmd(args):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=True, cwd=ROOT_DIR)
        return res.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def get_git_info():
    branch = run_cmd(["git", "rev-parse", "--abbrev-ref", HEAD := "HEAD"])
    status = run_cmd(["git", "status", "--porcelain"])
    last_commits = run_cmd(["git", "log", "-n", "3", "--oneline"])
    
    clean_status = "Clean" if not status else "Modified files:\n" + "\n".join([f"  - {line}" for line in status.split("\n")])
    return {
        "branch": branch,
        "status": clean_status,
        "commits": last_commits
    }

def get_db_stats():
    if not os.path.exists(DB_PATH):
        return None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get count of items
        cursor.execute("SELECT COUNT(*) FROM plan_macros")
        macros = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM policies")
        policies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM activities")
        activities = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        tasks = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM responsibles")
        responsibles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM change_logs")
        logs = cursor.fetchone()[0]

        # Calculate average progress of tasks
        cursor.execute("SELECT AVG(progress) FROM tasks")
        avg_progress = cursor.fetchone()[0]
        avg_progress = round(avg_progress, 2) if avg_progress is not None else 0.0
        
        conn.close()
        return {
            "macros": macros,
            "policies": policies,
            "activities": activities,
            "tasks": tasks,
            "responsibles": responsibles,
            "logs": logs,
            "avg_progress": avg_progress
        }
    except Exception as e:
        return {"error": str(e)}

def init_context():
    if os.path.exists(CONTEXT_FILE):
        print(f"El archivo context ya existe en {CONTEXT_FILE}. Usa 'update' para refrescarlo.")
        return
        
    git_info = get_git_info()
    db_stats = get_db_stats()
    
    db_str = ""
    if db_stats:
        if "error" in db_stats:
            db_str = f"Error al leer DB: {db_stats['error']}"
        else:
            db_str = (
                f"- **Macros creadas:** {db_stats['macros']}\n"
                f"- **Políticas registradas:** {db_stats['policies']}\n"
                f"- **Actividades:** {db_stats['activities']}\n"
                f"- **Tareas totales:** {db_stats['tasks']} (Progreso promedio: {db_stats['avg_progress']}%)\n"
                f"- **Personal registrado:** {db_stats['responsibles']}\n"
                f"- **Registros de auditoría (logs):** {db_stats['logs']}"
            )
    else:
        db_str = "No se detectó base de datos local SQLite (th_platform.sqlite)."

    content = f"""# Contexto de Proyecto — PA_TH Unitrópico
*Este archivo almacena de forma compacta el estado del proyecto para mantener la trazabilidad y reducir el consumo de tokens entre sesiones de IA.*

---

## 🏛️ Arquitectura del Sistema
- **Frontend:** Streamlit (`appth.py`)
- **Backend/ORM:** SQLAlchemy (`src/core/database.py`, `src/models/entities.py`)
- **Base de Datos:** SQLite local / PostgreSQL configurable via `.env`
- **Reportería:** ReportLab (PDF) con diseño institucional y Python-Docx (Word/Docx)

---

## 📌 Estado de Git y Ramificación
- **Rama Actual:** `{git_info['branch']}`
- **Estado de Trabajo:**
```text
{git_info['status']}
```
- **Últimos Commits:**
```text
{git_info['commits']}
```

---

## 📊 Estadísticas de la Base de Datos
{db_str}

---

## 🛠️ Estado de Fases de Desarrollo
- **Fase 1: UX + Funcionalidad Crítica:** ✅ 100% Completado.
- **Fase 2: Analítica y Trazabilidad:** ✅ 100% Completado (Gantt, Historial de Cambios, Justificación de Retraso, Evidencias, Excel).
- **Fase 3: Madurez Institucional:** ✅ 100% Completado (Cierre de Periodo, Configuración PostgreSQL, Reporte PDF Corporativo).
- **Fase 4: Gestión de Git y Contexto:** 🚧 En curso (Implementando control de contexto y políticas de ramas).

---

## 📜 Historial Reciente de Sesiones
- **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**: Inicialización del sistema de preservación de contexto y configuración del rol Experto en GitHub.
"""
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Creado archivo de contexto inicial en: {CONTEXT_FILE}")

def update_context(msg=None):
    if not os.path.exists(CONTEXT_FILE):
        print(f"El archivo {CONTEXT_FILE} no existe. Ejecuta 'init' primero.")
        return

    git_info = get_git_info()
    db_stats = get_db_stats()
    
    db_str = ""
    if db_stats:
        if "error" in db_stats:
            db_str = f"Error al leer DB: {db_stats['error']}"
        else:
            db_str = (
                f"- **Macros creadas:** {db_stats['macros']}\n"
                f"- **Políticas registradas:** {db_stats['policies']}\n"
                f"- **Actividades:** {db_stats['activities']}\n"
                f"- **Tareas totales:** {db_stats['tasks']} (Progreso promedio: {db_stats['avg_progress']}%)\n"
                f"- **Personal registrado:** {db_stats['responsibles']}\n"
                f"- **Registros de auditoría (logs):** {db_stats['logs']}"
            )
    else:
        db_str = "No se detectó base de datos local SQLite (th_platform.sqlite)."

    # Read current content to preserve custom parts (like Architecture, Phases, History)
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # We will reconstruct sections but preserve history log
    history_index = -1
    for i, line in enumerate(lines):
        if "## 📜 Historial Reciente de Sesiones" in line:
            history_index = i
            break
            
    history_lines = lines[history_index+1:] if history_index != -1 else []
    
    # Clean up empty lines at start of history
    while history_lines and history_lines[0].strip() == "":
        history_lines.pop(0)

    # Append new log message if provided
    if msg:
        new_log = f"- **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**: {msg}\n"
        history_lines.insert(0, new_log)
        # Keep history to last 15 entries to save tokens
        history_lines = history_lines[:15]

    new_content = f"""# Contexto de Proyecto — PA_TH Unitrópico
*Este archivo almacena de forma compacta el estado del proyecto para mantener la trazabilidad y reducir el consumo de tokens entre sesiones de IA.*

---

## 🏛️ Arquitectura del Sistema
- **Frontend:** Streamlit (`appth.py`)
- **Backend/ORM:** SQLAlchemy (`src/core/database.py`, `src/models/entities.py`)
- **Base de Datos:** SQLite local / PostgreSQL configurable via `.env`
- **Reportería:** ReportLab (PDF) con diseño institucional y Python-Docx (Word/Docx)

---

## 📌 Estado de Git y Ramificación
- **Rama Actual:** `{git_info['branch']}`
- **Estado de Trabajo:**
```text
{git_info['status']}
```
- **Últimos Commits:**
```text
{git_info['commits']}
```

---

## 📊 Estadísticas de la Base de Datos
{db_str}

---

## 🛠️ Estado de Fases de Desarrollo
- **Fase 1: UX + Funcionalidad Crítica:** ✅ 100% Completado.
- **Fase 2: Analítica y Trazabilidad:** ✅ 100% Completado (Gantt, Historial de Cambios, Justificación de Retraso, Evidencias, Excel).
- **Fase 3: Madurez Institucional:** ✅ 100% Completado (Cierre de Periodo, Configuración PostgreSQL, Reporte PDF Corporativo).
- **Fase 4: Gestión de Git y Contexto:** 🚧 En curso (Implementando control de contexto y políticas de ramas).

---

## 📜 Historial Reciente de Sesiones
{"".join(history_lines)}"""

    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Actualizado archivo de contexto en: {CONTEXT_FILE}")

def show_context():
    if not os.path.exists(CONTEXT_FILE):
        print("El archivo de contexto no existe todavía. Ejecuta 'init' para crearlo.")
        return
        
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want a very compact version for LLM consumption
    print("=== PROJECT CONTEXT SUMMARY ===")
    try:
        print(content)
    except UnicodeEncodeError:
        encoded_content = content.encode(sys.stdout.encoding or 'ascii', errors='backslashreplace').decode(sys.stdout.encoding or 'ascii')
        print(encoded_content)
    print("===============================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script para manejar la preservación de contexto en el proyecto.")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")
    
    subparsers.add_parser("init", help="Inicializa el archivo PROJECT_CONTEXT.md")
    
    update_parser = subparsers.add_parser("update", help="Actualiza el archivo PROJECT_CONTEXT.md")
    update_parser.add_argument("--msg", type=str, default=None, help="Mensaje para agregar al historial de cambios recientes")
    
    subparsers.add_parser("show", help="Muestra el contenido actual del contexto")
    
    args = parser.parse_args()
    
    if args.command == "init":
        init_context()
    elif args.command == "update":
        update_context(args.msg)
    elif args.command == "show":
        show_context()
    else:
        parser.print_help()
