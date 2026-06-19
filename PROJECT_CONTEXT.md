# Contexto de Proyecto — PA_TH Unitrópico
*Este archivo almacena de forma compacta el estado del proyecto para mantener la trazabilidad y reducir el consumo de tokens entre sesiones de IA.*

---

## 🏛️ Arquitectura del Sistema
- **Frontend:** Streamlit (`appth.py`)
- **Backend/ORM:** SQLAlchemy (`src/core/database.py`, `src/models/entities.py`)
- **Base de Datos:** SQLite local / PostgreSQL configurable via `.env`
- **Reportería:** ReportLab (PDF) con diseño institucional y Python-Docx (Word/Docx)

---

## 📌 Estado de Git y Ramificación
- **Rama Actual:** `task/excel-checklist`
- **Estado de Trabajo:**
```text
Modified files:
  - M data/th_platform.sqlite
  - ?? PRUEBAS_CHECKLIST.xlsx
  - ?? scripts/create_checklist_excel.py
```
- **Últimos Commits:**
```text
a6d5402 feat: fix dashboard bug, improve treemap readability, add new workers and create testing checklist
6949bf5 feat: implement project context preservation and git branch policy
581fa49 Resolve merge conflicts in .gitignore and README.md
```

---

## 📊 Estadísticas de la Base de Datos
- **Macros creadas:** 2
- **Políticas registradas:** 8
- **Actividades:** 86
- **Tareas totales:** 92 (Progreso promedio: 45.22%)
- **Personal registrado:** 7
- **Registros de auditoría (logs):** 0

---

## 🛠️ Estado de Fases de Desarrollo
- **Fase 1: UX + Funcionalidad Crítica:** ✅ 100% Completado.
- **Fase 2: Analítica y Trazabilidad:** ✅ 100% Completado (Gantt, Historial de Cambios, Justificación de Retraso, Evidencias, Excel).
- **Fase 3: Madurez Institucional:** ✅ 100% Completado (Cierre de Periodo, Configuración PostgreSQL, Reporte PDF Corporativo).
- **Fase 4: Gestión de Git y Contexto:** 🚧 En curso (Implementando control de contexto y políticas de ramas).

---

## 📜 Historial Reciente de Sesiones
- **2026-06-19 14:34:39**: Generada lista de chequeo en Excel (PRUEBAS_CHECKLIST.xlsx) para pruebas detalladas de perfiles y secciones
- **2026-06-19 12:01:43**: Creados 5 trabajadores nuevos en base de datos. Generado archivo de checklist PRUEBAS_CHECKLIST.md en la raiz del proyecto.
- **2026-06-19 11:47:19**: Aumentado el tamaño de la letra y truncadas las descripciones de Estrategia a 50 caracteres en el grafico Treemap de Desglose Estrategico del Dashboard
- **2026-06-19 11:44:39**: Corregido error UnboundLocalError en src/ui/views/dashboard.py removiendo importaciones locales redundantes de numpy y plotly
- **2026-06-19 11:39:38**: Realizadas pruebas completas dry-run exitosas de los servicios de calculo, autenticacion y todos los exportadores (PDF, Word, Excel). Ignorado directorio scratch/ en .gitignore.
- **2026-06-19 11:32:27**: Configurado el entorno de preservación de contexto y políticas de ramas de Git en la rama task/context-and-git-skills
- **2026-06-19 11:32:03**: Inicialización del sistema de preservación de contexto y configuración del rol Experto en GitHub.
