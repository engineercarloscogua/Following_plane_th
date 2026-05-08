# Plataforma TH - Unitrópico

Sistema Integral de Seguimiento Estratégico de Talento Humano. Diseñado para centralizar y automatizar el seguimiento del Plan Anual de Trabajo (PAT).

## Requisitos
- **Python 3.12**
- Streamlit
- SQLAlchemy 2.0 (SQLite para pruebas locales)

## Instalación Local

1. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación:
   ```bash
   streamlit run appth.py
   ```

3. Credenciales iniciales:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`

## Estructura del Proyecto
- `src/core`: Configuración de base de datos y utilidades base.
- `src/models`: Modelos de datos (SQLAlchemy 2.0).
- `src/services`: Lógica de negocio y cálculos de progreso.
- `src/ui`: Interfaz de usuario modular.

## Despliegue en Streamlit Cloud
1. Subir a GitHub.
2. Conectar repositorio en [Streamlit Cloud](https://share.streamlit.io/).
3. Configurar `appth.py` como punto de entrada.
