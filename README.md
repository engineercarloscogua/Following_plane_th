# 🏛️ Sistema Integral de Seguimiento Estratégico de Talento Humano - Unitrópico

## 📝 Descripción
Plataforma avanzada de Business Intelligence y gestión operativa diseñada para el seguimiento del **Plan Estratégico de Talento Humano**. El sistema permite la gestión de una jerarquía estratégica de 5 niveles, desde la visión macro hasta la ejecución de tareas individuales.

## 🚀 Características Principales
- **Jerarquía Multinivel**: Gestión de Plan Macro, Políticas, Programas, Actividades y Tareas.
- **Dashboard Ejecutivo**: Visualización de alto impacto con radares de cumplimiento, mapas de red y análisis de tendencia.
- **Dashboard Personal**: Seguimiento de productividad por responsable y auditoría de eficiencia.
- **Mosaico TH**: Explorador jerárquico auto-retraíble para una visión 360° de la entidad.
- **Centro de Alertas**: Monitoreo de tareas vencidas, próximas a vencer y auditoría de puntualidad.
- **Clonador Estratégico**: Duplicación completa de estructuras para nuevos años fiscales con un solo clic.

## 🛠️ Tecnologías Utilizadas
- **Python 3.12**
- **Streamlit**: Framework para la interfaz de usuario.
- **SQLAlchemy**: ORM para la gestión de base de datos (SQLite/PostgreSQL).
- **Plotly**: Motor de visualizaciones interactivas de alta gama.
- **Pandas**: Procesamiento y análisis de datos.

## 📂 Estructura del Proyecto
```text
PA_TH_Unitropico/
├── appth.py                # Punto de entrada principal
├── src/
│   ├── core/               # Configuración central (DB)
│   ├── models/             # Entidades de base de datos
│   ├── services/           # Lógica de negocio (Cálculos, Auth)
│   └── ui/
│       └── views/          # Módulos de interfaz (Dashboards, Admin, etc.)
├── assets/                 # Estilos CSS e imágenes institucionales
└── data/                   # Almacenamiento de base de datos local
```

## 🔧 Instalación y Ejecución
1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Ejecutar la aplicación:
   ```bash
   streamlit run appth.py
   ```

## 🔐 Seguridad
El sistema implementa autenticación basada en roles (**Admin** y **Supervisor**), garantizando que la configuración estratégica sea protegida mientras se facilita la operación diaria.

---
**Desarrollado para la excelencia institucional en Gestión Humana.**
