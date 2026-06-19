# Guía de Pruebas y Lista de Chequeo — PA_TH Unitrópico

Este documento proporciona una lista de chequeo (checklist) detallada con las credenciales y pasos necesarios para verificar el correcto funcionamiento de toda la plataforma de Talento Humano en sus tres roles principales: **Administrador (Admin)**, **Supervisor** y **Trabajador (Worker)**.

---

## 🔑 Credenciales de Acceso

Usa estas cuentas para iniciar sesión en la pantalla de login del sistema:

| Nombre / Cargo | Rol | Usuario | Contraseña |
| :--- | :--- | :--- | :--- |
| **Administrador General** | **Admin** | `admin` | `admin123` |
| **Lilia Andrea Nocua Neme** (Jefe de Oficina) | **Supervisor** | `lilia.nocua` | `lilia123` |
| **Rosaura Andrea Ramirez** (Profesional TH) | **Worker** | `rosaura.ramirez` | `rosaura123` |
| **Laura Vanesa Cely** (Profesional TH) | **Worker** | `laura.cely` | `laura123` |
| **Claudia America Garcia** (Profesional TH) | **Worker** | `claudia.garcia` | `claudia123` |
| **Leidy Yamile Garcia** (Profesional TH) | **Worker** | `leidy.garcia` | `leidy123` |
| **Yusney Garcia** (Profesional TH) | **Worker** | `yusney.garcia` | `yusney123` |
| **Yenny Cardenas** (Profesional TH) | **Worker** | `yenny.cardenas` | `yenny123` |

---

## 📋 Lista de Chequeo de Pruebas

### 1. Pruebas de Acceso y Menú Lateral por Rol

* [ ] **Paso 1.1: Ingreso de Administrador**
  * Inicia sesión con el usuario `admin` / `admin123`.
  * **Verificación:** Debes ver en el sidebar izquierdo exactamente 5 pestañas:
    1. `🏠 Inicio` (Dashboard corporativo)
    2. `🧩 Estructura TH` (Jerarquía del Plan de Acción)
    3. `📄 Exportar Reporte` (Word, Excel, PDF)
    4. `🧐 Seguimiento de Tareas` (Gestión global de tareas)
    5. `⚙️ Configuración` (Administración de periodos, usuarios y logs)
* [ ] **Paso 1.2: Ingreso de Supervisor**
  * Cierra sesión e ingresa con el usuario `lilia.nocua` / `lilia123`.
  * **Verificación:** Debes ver únicamente 2 pestañas en el menú lateral:
    1. `🏠 Inicio` (Dashboard enfocado en su equipo)
    2. `🧐 Gestión de Tareas` (Pestañas de "Mi Equipo" y tabla filtrable de asignaciones)
* [ ] **Paso 1.3: Ingreso de Trabajador**
  * Cierra sesión e ingresa con cualquiera de los usuarios Worker (ej. `laura.cely` / `laura123`).
  * **Verificación:** Debes ver única y exclusivamente la pestaña `✅ Mis Tareas` en el sidebar.

---

### 2. Flujo del Trabajador (Worker) — Reporte de Avance

* [ ] **Paso 2.1:** Inicia sesión con la cuenta de un trabajador (ej. `rosaura.ramirez` o `laura.cely`).
* [ ] **Paso 2.2: Organización de Tareas**
  * **Verificación:** Tus tareas deben estar organizadas automáticamente por su urgencia (Vencidas 🔴, Esta semana 🟡, Restantes 📋). Las tareas que ya estén cumplidas (100%) deben listarse al final en una sección colapsada.
* [ ] **Paso 2.3: Actualización de Hito**
  * Ubica una tarea que esté en 0% (Pendiente).
  * Usa el deslizador (slider) para mover el avance a un valor intermedio (ej. 70%).
  * Escribe una observación en el campo de texto.
  * Agrega un enlace de evidencia (ej. `https://drive.google.com/drive/folders/mi-evidencia`).
  * Haz clic en **Guardar Avance**.
  * **Verificación:** La tarea debe cambiar automáticamente su etiqueta de estado a **"En Proceso"**.
* [ ] **Paso 2.4: Completar Tarea**
  * Modifica el slider de la misma tarea a **100%** y guarda.
  * **Verificación:** El estado de la tarea debe cambiar a **"Cumplida"** y el registro debe moverse automáticamente a la sección inferior colapsada "Historial de Tareas Cumplidas".

---

### 3. Flujo del Supervisor — Monitoreo y Auditoría de Retrasos

* [ ] **Paso 3.1:** Inicia sesión como `lilia.nocua` / `lilia123`.
* [ ] **Paso 3.2: Vista de Equipo**
  * Ve a la pestaña `Mi Equipo` (en el Inicio de su menú).
  * **Verificación:** Debes visualizar la lista de personal a cargo (Rosaura, Laura, Claudia, etc.) con sus estadísticas de tareas (Totales, Cumplidas, Vencidas) y una barra de progreso acumulado con semáforo.
* [ ] **Paso 3.3: Filtros de Gestión**
  * Ve a la pestaña `Gestión de Tareas`.
  * Usa los filtros horizontales (por ejemplo, filtrar por la política "Integridad" o por responsable "Laura Vanesa Cely").
  * **Verificación:** La tabla inferior debe responder mostrando solo los registros filtrados en tiempo real.
* [ ] **Paso 3.4: Obligatoriedad de Justificación por Retraso**
  * Busca una tarea que se encuentre **Vencida** (fecha límite anterior a hoy y progreso menor al 100%).
  * Haz clic en el botón de editar (`✏️`) para abrir la ventana modal.
  * Modifica cualquier dato (observaciones o progreso) e intenta guardar dejando el campo **"Justificación de Retraso"** vacío.
  * **Verificación:** El sistema debe mostrar un mensaje de error advirtiendo que la justificación es obligatoria por estar fuera de la fecha límite y no te permitirá guardar.
  * Rellena la justificación de retraso y guarda. El cambio se registrará con éxito.

---

### 4. Dashboards e Indicadores Visuales (Admin)

* [ ] **Paso 4.1:** Inicia sesión como `admin` / `admin123`.
* [ ] **Paso 4.2: Alertas Críticas**
  * **Verificación:** Si hay tareas vencidas o por vencer en los próximos 7 días, debes ver banners colapsables con colores (Rojo 🔴 / Amarillo 🟡) al inicio del Dashboard con el listado detallado.
* [ ] **Paso 4.3: Velocímetro y Gráficos**
  * **Verificación:** Se debe mostrar el velocímetro de avance consolidado con el color correspondiente del semáforo. A su derecha, el gráfico de barras horizontales de Plotly debe listar el cumplimiento por Política.
* [ ] **Paso 4.4: Desglose Estratégico (Treemap)**
  * **Verificación:** Debes visualizar el mapa de calor (Treemap) interactivo. Los títulos de las estrategias deben ser legibles y estar acortados a un máximo de 50 caracteres (evitando letras microscópicas), y al pasar el cursor sobre cada recuadro debe desplegarse el avance porcentual.

---

### 5. Configuración de Cierre y Trazabilidad (Admin)

* [ ] **Paso 5.1:** En la sesión de administrador, ve a `Configuración` -> pestaña `Continuidad`.
* [ ] **Paso 5.2: Trazabilidad de Auditoría**
  * **Verificación:** Debe mostrarse la tabla de historial de cambios. Todos los cambios que realizaste en los pasos anteriores (como la actualización del progreso de Rosaura o la justificación de Lilia) deben estar detallados indicando quién lo cambió, qué campo, el valor antiguo y el valor nuevo.
* [ ] **Paso 5.3: Bloqueo de Período**
  * Haz clic en el botón **"🔒 Cerrar y Bloquear Periodo"** correspondiente al año 2025.
  * **Verificación:** El estado del periodo debe pasar a "Bloqueado".
* [ ] **Paso 5.4: Validar Bloqueo de Escritura**
  * Sin cerrar sesión, ve a la pestaña `Seguimiento de Tareas` o inicia sesión como Worker (`rosaura.ramirez`).
  * Intenta editar cualquier tarea o añadir evidencias.
  * **Verificación:** Todos los campos de edición, sliders y botones de guardado deben estar deshabilitados (modo Solo Lectura), mostrando una alerta de que el periodo se encuentra bloqueado para auditoría.
  * *Una vez probado, regresa a Configuración como Admin y haz clic en "🔓 Desbloquear Periodo" para habilitar la edición.*

---

### 6. Generación y Descarga de Reportes Oficiales

* [ ] **Paso 6.1:** Ve a la pestaña `Exportar Reporte`.
* [ ] **Paso 6.2:** Configura el filtro por periodo (ej. "Año Completo" o "Mes de Enero").
* [ ] **Paso 6.3: Probar Reporte Word**
  * Haz clic en **"Procesar Datos para Reporte Word"** y luego descarga el archivo `.docx` resultante.
  * **Verificación:** Ábrelo y confirma la portada con el verde institucional (`#00594e`), la introducción y las tablas de actividades cebra con las observaciones y links de evidencias de tu equipo.
* [ ] **Paso 6.4: Probar Excel Ejecutivo**
  * Pestaña Excel: Haz clic en **"Generar Excel Ejecutivo"** y descarga el archivo `.xlsx`.
  * **Verificación:** Ábrelo y comprueba que contenga 4 hojas de trabajo ("Resumen", "Detalle", "Equipo", "Trazabilidad") con los colores y fórmulas de avance consolidados.
* [ ] **Paso 6.5: Probar PDF Institucional**
  * Pestaña PDF: Haz clic en **"Generar PDF Oficial"** y descarga el archivo `.pdf`.
  * **Verificación:** Ábrelo y comprueba que contenga el membrete institucional con logo de Unitrópico, semáforos en tablas y la sección final de firmas de aprobación en orden.
