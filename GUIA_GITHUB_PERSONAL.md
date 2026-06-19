# Guía de Migración y Uso del GitHub Personal
Este documento detalla paso a paso el proceso para configurar, migrar y realizar de manera exclusiva el seguimiento y almacenamiento de este proyecto en tu repositorio personal de GitHub vinculado al correo **engineer.carloscogua@gmail.com**, quitando la asociación institucional de `talentohumano`.

---

## Paso 1: Configurar la Identidad de Git Local
Para asegurar que todos los cambios futuros se registren a nombre de tu perfil personal, debes cambiar la configuración del usuario en la carpeta local del proyecto.

Abre la terminal en la raíz del proyecto y ejecuta:

```bash
# Cambiar el correo local para este repositorio específico
git config --local user.email "engineer.carloscogua@gmail.com"

# Cambiar el nombre de usuario que aparecerá en los commits
git config --local user.name "Carlos Cogua"
```

*Nota: Al usar `--local` nos aseguramos de que esto solo afecte a esta carpeta y no a otros proyectos institucionales de tu equipo.*

---

## Paso 2: Crear el Repositorio en tu GitHub Personal
1. Inicia sesión en **[GitHub](https://github.com)** usando tu cuenta de correo personal: `engineer.carloscogua@gmail.com`.
2. En la parte superior derecha, haz clic en el botón de **`+`** y selecciona **New repository** (Nuevo repositorio).
3. Configura el repositorio:
   * **Repository name:** `PA_TH_Unitropico`
   * **Description:** Sistema de Seguimiento de Gestión Estratégica de Talento Humano.
   * **Public/Private:** Elige según tu preferencia (se recomienda **Private** para proteger los datos institucionales sembrados).
   * **IMPORTANTE:** No marques ninguna casilla en "Initialize this repository with" (*Add a README file*, *Add .gitignore*, o *Choose a license*). El repositorio debe quedar vacío.
4. Haz clic en **Create repository**.
5. Copia la URL HTTPS que se genera. Será similar a:
   `https://github.com/TU_USUARIO_PERSONAL/PA_TH_Unitropico.git`

---

## Paso 3: Actualizar el Repositorio Remoto (Cambiar Origin)
Actualmente, el proyecto apunta al servidor institucional de GitHub. Debemos re-direccionar la ruta para que apunte al repositorio que acabas de crear:

```bash
# Reemplazar la URL institucional por la de tu GitHub personal
git remote set-url origin https://github.com/TU_USUARIO_PERSONAL/PA_TH_Unitropico.git
```
*(Reemplaza `TU_USUARIO_PERSONAL` por tu nombre de usuario exacto de GitHub personal).*

Puedes verificar que el cambio se aplicó correctamente ejecutando:
```bash
git remote -v
```

---

## Paso 4: Configurar la Autenticación (Evitar Conflictos de Credenciales)
Dado que estás en Windows, el sistema guarda las credenciales institucionales de `carloscogua@talentohumano` en su llavero de contraseñas. Para evitar errores de "Permiso denegado", debes elegir una de estas dos opciones:

### Opción Recomendada: Autenticación por Token de Acceso Personal (PAT)
1. En tu cuenta de GitHub personal, ve a tu foto de perfil (arriba a la derecha) -> **Settings** -> **Developer settings** (al final de la barra izquierda) -> **Personal access tokens** -> **Tokens (classic)**.
2. Haz clic en **Generate new token (classic)**.
3. Rellena los datos:
   * **Note:** `Acceso Local PA_TH`
   * **Expiration:** Elige la duración (ej. 90 días o sin expiración).
   * **Scopes:** Marca obligatoriamente la casilla **`repo`** (permite leer y escribir en repositorios privados).
4. Haz clic en **Generate token** en la parte inferior.
5. **Copia el token generado** inmediatamente (empieza por `ghp_...`). Si cierras la página, no podrás volver a verlo.
6. Actualiza tu URL remota local integrando tu usuario y el token de acceso para que Git no solicite contraseñas al subir cambios:
   ```bash
   git remote set-url origin https://TU_USUARIO_PERSONAL:TU_TOKEN_DE_GITHUB@github.com/TU_USUARIO_PERSONAL/PA_TH_Unitropico.git
   ```

### Opción Alternativa: Limpiar el Llavero de Windows
1. En la barra de búsqueda de Windows escribe **Administrador de Credenciales** (Credential Manager) y ábrelo.
2. Ve a la pestaña **Credenciales de Windows**.
3. En la sección "Credenciales genéricas", busca los registros que contengan `git:https://github.com` o `github.com` asociados a la cuenta institucional.
4. Selecciónalos y haz clic en **Quitar** (Remove).
5. La siguiente vez que ejecutes un comando `push`, Windows abrirá una interfaz en tu navegador para que inicies sesión directamente con tu correo personal.

---

## Paso 5: Realizar el Primer Envío (Push) de Cambios
Una vez configurado el remoto y la autenticación, agrega tus archivos locales, haz un commit y sube los cambios:

```bash
# 1. Agregar dependencias, configuraciones y el código del sistema (excluyendo base de datos y temporales)
git add requirements.txt .env.example appth.py src/

# 2. Confirmar los cambios
git commit -m "Migracion del sistema al repositorio personal con mejoras Fase 1, 2 y 3"

# 3. Subir los cambios a la rama principal (se creará la rama remota)
git push -u origin main
```

---

## Buenas Prácticas
1. **Archivo .gitignore:** Asegúrate de que tu base de datos local y claves del entorno no se suban al repositorio público. Tu archivo `.gitignore` debe contener al menos:
   ```text
   data/*.sqlite
   .env
   __pycache__/
   .streamlit/
   scratch/informe_2025_extracted.txt
   ```
2. **Uso Diario:** A partir de este momento, cada vez que hagas cambios y quieras guardarlos, solo debes ejecutar de forma estándar:
   ```bash
   git add .
   git commit -m "descripción de tus cambios"
   git push
   ```
   El sistema los enviará exclusivamente a tu repositorio personal configurado en el **Paso 4**.
