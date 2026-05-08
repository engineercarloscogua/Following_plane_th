# 🚀 Guía de Despliegue en Producción: Plataforma TH Unitrópico

Esta guía detalla los pasos para poner tu plataforma en línea de forma gratuita utilizando **Streamlit Cloud**.

---

## 📋 Requisitos Previos
1.  **Cuenta en GitHub**: Debes tener una cuenta en [github.com](https://github.com).
2.  **Cuenta en Streamlit Cloud**: Regístrate en [share.streamlit.io](https://share.streamlit.io) usando tu cuenta de GitHub.

---

## 🛠️ Paso 1: Preparar tu Repositorio en GitHub

1.  Crea un nuevo repositorio en GitHub llamado `PA_TH_Unitropico`.
2.  Sube todos los archivos de tu proyecto local a este repositorio. 
    *   **IMPORTANTE**: Asegúrate de incluir la carpeta `assets/`, la carpeta `src/`, el archivo `appth.py` y el `requirements.txt`.
    *   **Nota**: No es necesario subir el archivo `.sqlite` si quieres que la base de datos se inicie limpia en la nube.

---

## 🌐 Paso 2: Despliegue en Streamlit Cloud

1.  Inicia sesión en [share.streamlit.io](https://share.streamlit.io).
2.  Haz clic en el botón **"New app"**.
3.  Selecciona tu repositorio (`PA_TH_Unitropico`), la rama (`main`) y el archivo principal (`appth.py`).
4.  Haz clic en **"Deploy!"**.

---

## 🔐 Paso 3: Configuración de Seguridad (Opcional)

Si deseas cambiar las contraseñas o configurar secretos en el futuro:
1.  En el panel de tu app en Streamlit Cloud, ve a **Settings** > **Secrets**.
2.  Aquí puedes definir variables de entorno si decides no usar el archivo `.env` local.

---

## ⚠️ Advertencia sobre Persistencia (SQLite)

**IMPORTANTE**: Streamlit Cloud es una plataforma "Serverless". Esto significa que:
*   Si el sistema se reinicia (por inactividad o actualización), el archivo `th_platform.sqlite` podría volver a su estado inicial si no se maneja una base de datos externa.
*   **Recomendación**: Para un uso institucional a largo plazo con datos críticos, se recomienda conectar el sistema a una base de datos en la nube (como **PostgreSQL** o **Supabase**), los cuales también tienen capas gratuitas.

---

## ✅ Resumen de Archivos Clave para Producción
*   `appth.py`: Punto de entrada.
*   `requirements.txt`: Lista de librerías para que el servidor las instale automáticamente.
*   `assets/`: Logos y estilos CSS.
*   `src/`: Toda la lógica de negocio y modelos.

---

¡Felicidades! Tu plataforma estará disponible en una URL pública (ej: `https://tu-app.streamlit.app`) para que todos en la universidad puedan acceder desde cualquier lugar.
