# Arquitectura de Seguridad y Mitigación de Vulnerabilidades

**Sistema Integral de Seguimiento Estratégico de Talento Humano**

Este documento detalla las políticas, configuraciones y mecanismos defensivos implementados a nivel de código y servidor para garantizar la confidencialidad, integridad y disponibilidad (Tríada CIA) de la plataforma institucional. Todas las medidas se han desarrollado siguiendo las directrices del **Top 10 de OWASP**.

---

## 1. Protección contra Inyección de Código (Cross-Site Scripting - XSS)

### El Vector de Ataque
Dado que la plataforma utiliza interfaces visuales altamente personalizadas (insignias, barras de progreso y tarjetas de información interactivas), se requería el renderizado de HTML directo a través de la función de Streamlit `unsafe_allow_html=True`. Si un actor malicioso o una cuenta comprometida insertaba código JavaScript oculto (ej. `<script>...`) en el nombre de una Tarea o en una Observación, el sistema lo renderizaba, permitiendo el robo de cookies de sesión (Session Hijacking).

### La Contramedida Aplicada (Sanitización Quirúrgica)
Se ha implementado una barrera de sanitización obligatoria en todas las vistas (`admin.py`, `alerts.py`, `dashboard.py`, `mosaico.py`, `operations.py`, `reports.py`, `supervisor.py`).
Se utiliza la función nativa de Python `html.escape()`, la cual intercepta y convierte caracteres especiales (`<`, `>`, `&`, `"`, `'`) en secuencias de escape seguras (ej. `&lt;`). 

*   **Ejemplo de Mitigación**: Si el nombre ingresado es `<script>alert('XSS')</script>`, el motor de interfaz no lo ejecutará como código, sino que lo convertirá y mostrará textualmente y de manera inofensiva como texto plano en la tarjeta del usuario.

---

## 2. Defensa contra Falsificación de Peticiones en Sitios Cruzados (CSRF)

### El Vector de Ataque
Sin protección CSRF, un atacante externo podría crear una página web o un enlace engañoso y convencer a un Administrador activo para que haga clic en él. Como el administrador ya tiene una sesión validada en su navegador, el enlace malicioso podría enviar peticiones invisibles a la plataforma de Talento Humano en nombre del administrador (por ejemplo, "Eliminar el Plan Macro 2026").

### La Contramedida Aplicada (Tokens XSRF)
Se ha habilitado la bandera `enableXsrfProtection = true` a nivel de servidor (en `config.toml`). 
Esta protección obliga al servidor de la aplicación a generar un "token criptográfico único e irrepetible" para cada sesión legítima. Cualquier petición que modifique datos en la base de datos debe contener este token exacto. Los scripts maliciosos alojados en otros sitios web no tienen acceso a este token, por lo que el servidor rechaza automáticamente el ataque.

---

## 3. Barreras de Intercambio de Recursos de Origen Cruzado (CORS)

### La Contramedida Aplicada
Se ha activado `enableCORS = true` en el archivo de configuración del servidor.
El protocolo CORS (Cross-Origin Resource Sharing) es un mecanismo de seguridad implementado a nivel de los navegadores web modernos y el servidor de la aplicación. Al habilitarlo, indicamos explícitamente que la API interna y el sistema de websockets de nuestra aplicación **sólo aceptarán conexiones provenientes de nuestro propio dominio de confianza**. Se bloquean tajantemente todos los intentos de servidores remotos o consolas externas que intenten interactuar directamente con el núcleo de datos del sistema.

---

## 4. Escudos Anti-Scraping y Mitigación de Fuerza Bruta (Anti-Bots)

### El Vector de Ataque
Los sistemas de información estratégica son blanco frecuente de extracción de datos automatizada ("Web Scraping"). Estos atacantes utilizan "Bots" (scripts programados) que navegan el sitio a velocidades inhumanas copiando toda la información. Para poder hacer esto en un sistema cerrado, el bot primero debe adivinar una contraseña ("Ataque de Fuerza Bruta" mediante diccionarios).

### Las Contramedidas Aplicadas
Se ha construido un blindaje de dos capas para neutralizar ataques automatizados:

1.  **Delay Algorítmico (Blindaje de Inicio de Sesión)**:
    En el motor de autenticación (`src/services/auth.py`), se ha inyectado una demora intencional controlada (`time.sleep`) que se activa única y exclusivamente cuando un usuario se equivoca de credenciales. 
    *   *Por qué funciona*: Un retardo de apenas 1.5 segundos es totalmente imperceptible e inofensivo para un humano que se equivocó tecleando, pero **destruye matemáticamente** a un bot atacante, obligándolo a tardar años en intentar descifrar las miles de combinaciones de contraseña posibles, en lugar de hacerlo en cuestión de minutos.
2.  **Ofuscación del DOM y Ceguera de Extracción (Blindaje UI)**:
    Mediante la inyección de estilos de cascada avanzados (`assets/style.css`), se ha bloqueado la interacción del nivel de abstracción del ratón (`user-select: none;`). Esto imposibilita el copiado manual y "ciega" a los bots de extracción simple (como Selenium o Beautiful Soup) impidiéndoles recorrer las jerarquías de las tarjetas de forma sencilla. Adicionalmente, se ocultó la infraestructura visible de Streamlit (el menú superior y el pie de página), dificultando que un atacante reconozca la tecnología subyacente y aplique vulnerabilidades conocidas sobre ella.

---

## 5. Criptografía y Persistencia de Sesión

### Hasheo de Contraseñas Seguras
Toda contraseña procesada por el sistema (`AuthService`) es encriptada utilizando el estándar industrial criptográfico **Bcrypt**.
Bcrypt no solo encripta la contraseña usando cifrados de un solo sentido (que no pueden ser desencriptados ni siquiera por el Administrador de bases de datos), sino que aplica una técnica llamada **"Salting"**. El "Salting" adjunta una cadena de caracteres aleatoria y única a cada contraseña antes de cifrarla, lo cual inmuniza a la plataforma frente a ataques masivos de recuperación de contraseñas conocidos como "Tablas Arcoíris" (Rainbow Tables).

### Manejo de Estados Temporales
Las sesiones activas de Administradores y Supervisores se mantienen aisladas y protegidas en la memoria del hilo de ejecución mediante el objeto seguro `st.session_state`. El nivel de autorización del usuario ("role") se verifica de forma estricta antes del acceso y renderizado de cada módulo administrativo de la plataforma, evitando intrusiones mediante manipulación de URLs.
