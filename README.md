# SICEME - Control Epidemiológico y Estadístico Médico 🏥

![Version](https://img.shields.io/badge/version-1.5.0-blue)
![Django](https://img.shields.io/badge/Framework-Django%205.0-green)
![Security](https://img.shields.io/badge/Security-Advanced%20Blindado-red)
![License](https://img.shields.io/badge/License-Proprietary-gold)

**SICEME** es una plataforma integral de gestión y análisis de morbilidad diseñada para instituciones médicas que requieren un control estricto, reportes dinámicos y una seguridad de grado industrial. Este sistema permite centralizar la información de emergencias, consultas especializadas y ecosonogramas, transformando datos crudos en inteligencia médica visual.

---

## 🚀 Características Principales

### 1. Gestión de Morbilidad Multimodular
*   **Emergencias:** Registro rápido y eficiente de ingresos de urgencia.
*   **Especialistas:** Control detallado de consultas por especialidad con diagnósticos precisos.
*   **Ecosonogramas:** Seguimiento especializado con categorización de estudios.
*   **Pacientes No Asistidos:** Monitoreo de inasistencias para optimizar la carga médica.

### 2. Inteligencia de Datos y Reportes Premium
*   **Dashboard Dinámico:** Gráficos interactivos (Chart.js) con etiquetas de datos automáticas.
*   **Reportes de Periodo Personalizados:** Generación de análisis comparativos por mes y año.
*   **Ranking de Especialidades:** Sistema visual con medallas de honor para las áreas de mayor impacto.
*   **Exportación Profesional:** Descarga de reportes en Excel y gráficos en formato imagen (PNG) con un solo clic.

### 3. Seguridad y Blindaje (Security-First)
*   **Protección Avanzada:** Sistema inmune a Inyecciones SQL y ataques XSS (Cross-Site Scripting).
*   **Control de Acceso (RBAC):** Roles definidos (Admin, Especialista, Público) con permisos estrictos.
*   **Bitácora de Auditoría:** Registro detallado de cada acción realizada en el sistema (quién, qué, cuándo y desde dónde).
*   **Soft Delete:** Los datos nunca se eliminan definitivamente; se archivan para preservar la integridad legal de la información médica.
*   **2FA & Bloqueo:** Verificación por OTP y bloqueo automático de cuentas tras intentos fallidos.

---

## 🛠 Stack Tecnológico
*   **Backend:** Python 3.x + Django 5.x
*   **Frontend:** HTML5 Semántico, CSS3 Premium (Aesthetics Focused), JavaScript ES6+.
*   **Gráficos:** Chart.js con plugins de datalabels.
*   **Servidor Local:** Waitress (Producción) / Django Dev Server.
*   **Middleware:** WhiteNoise para gestión optimizada de archivos estáticos.

---

## 📋 Requisitos del Sistema
*   Python 3.10 o superior.
*   Navegador moderno (Chrome, Edge, Firefox, Opera).
*   Entorno Windows (para el despliegue automático mediante Scripts).

---

## 📦 Instalación y Configuración Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/Morbilidades.git
   cd Morbilidades
   ```

2. **Crear y activar entorno virtual:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   Crea un archivo `.env` basado en el ejemplo proporcionado con tu `SECRET_KEY` y credenciales de correo.

5. **Preparar base de datos:**
   ```bash
   python manage.py migrate
   ```

---

## 🖥 Despliegue en Producción Local (Modo Silencioso)

Para un uso profesional en una computadora de escritorio, se han incluido scripts de automatización:

1.  **Lanzador Manual (`start_server.bat`):** Ejecuta el servidor mostrando la consola para depuración.
2.  **Lanzador Silencioso (`Iniciar_Sistema_Oculto.vbs`):**
    *   Ejecuta el sistema en segundo plano sin mostrar ventanas de terminal.
    *   Abre automáticamente el navegador en la dirección local.
    *   **Recomendación:** Crear un acceso directo de este archivo en el escritorio para acceso rápido.

---

## 🌐 Despliegue en Hosting (Dominio .com)
El sistema está configurado para ser desplegado en servicios como Heroku, Railway o VPS (DigitalOcean).
*   Asegúrese de cambiar `DEBUG = False` en las variables de entorno.
*   Configure su dominio en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` dentro de `settings.py`.

---

**Desarrollado con pasión por la excelencia médica y tecnológica.**
