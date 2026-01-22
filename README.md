# SGD-DLP (MVP)

Sistema de Gestión Documental con funciones de Prevención de Pérdida de Datos (DLP). Prototipo académico construido en Django + DRF con UI en Django Templates/Bootstrap; pensado para demostrar detección por regex, clasificación y trazabilidad.

## Características principales
- Carga y análisis de documentos (.txt, .docx, .pdf) con extracción de texto y normalización básica.
- Reglas regex configurables (modelo `RegexRule`) asociadas a categorías; severidad 1-5.
- Clasificación automática por categoría dominante y cálculo de `risk_score` (suma de severidades, máx 100).
- Generación de alertas si existen hallazgos y se supera el umbral de severidad o riesgo (`PolicyConfig`: `severity_threshold`, `risk_score_threshold`). Ciclo OPEN → ACK → CLOSED → REOPEN con auditoría.
- Auditoría centralizada (`AuditEvent`) de eventos clave: DOC_UPLOADED, TEXT_EXTRACTED, SCAN_DONE, ALERT_CREATED, ALERT_ACK, ALERT_CLOSED, ALERT_REOPENED.
- Enmascarado visual de hallazgos en la UI (filtro `mask`); API REST devuelve coincidencias completas.
- Panel web operativo: dashboard, lista/detalle de documentos, carga con escaneo, bandeja de alertas y auditoría.
- API REST autenticada por sesión (DRF) para carga/escaneo y consultas.

## Arquitectura rápida
- Django 5.0 + DRF; apps: `policies` (categorías, reglas, config), `documents` (almacenamiento, hallazgos, escaneo), `alerts` (alertas y permisos), `audit` (eventos), `ui` (vistas y plantillas).
- Base de datos SQLite por defecto; almacenamiento de archivos en `media/docs/`.
- Idioma `es-ec`, zona horaria `America/Guayaquil`, autenticación de sesiones de Django.

## Puesta en marcha
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py createsuperuser`
6. Semillas:
   - `python manage.py seed_policies` crea categorías/regex de ejemplo (cédula, RUC, tarjeta).
   - `python manage.py seed_roles` crea grupos Administrador, Responsable de Seguridad y Usuario Técnico con permisos asignados.
7. Ejecutar: `python manage.py runserver`
8. Accesos: UI `http://127.0.0.1:8000/`, Admin `http://127.0.0.1:8000/admin/`.

## Roles y permisos (semillas)
- Administrador: acceso total a documentos, hallazgos (incl. permiso `view_sensitive_finding`), alertas, políticas y auditoría; puede ACK/CLOSE.
- Responsable de Seguridad: ver documentos/hallazgos, ver y cambiar/ack alertas, ver auditoría.
- Usuario Técnico: cargar y ver documentos; ver estado de alertas; no puede atender alertas ni ver auditoría global. (UI muestra hallazgos enmascarados para todos).

## Flujo de trabajo
1) Usuario autenticado carga un archivo desde la UI o `POST /api/documents/upload-scan/`.
2) Se extrae texto (txt/docx/pdf), se ejecutan regex habilitadas y se registran `Finding`.
3) Se asigna categoría dominante y `risk_score`; se registran eventos `TEXT_EXTRACTED` y `SCAN_DONE`.
4) Si corresponde, se crea `Alert` y evento `ALERT_CREATED`.
5) Operaciones de ACK/CLOSE/REOPEN en UI registran eventos de auditoría.
6) Bandeja de auditoría permite filtrar por tipo, usuario, fechas y texto.

## API rápida (DRF, sesión)
- `POST /api/documents/upload-scan/` (multipart `original_name`, `file`): sube y escanea; devuelve resumen y hallazgos.
- `GET /api/documents/<id>/`: detalle de documento + hallazgos.
- `GET /api/policies/categories/` y `GET /api/policies/rules/`: catálogos de políticas.
- `GET /api/alerts/`: listado simple de alertas.
- `GET /api/audit/`: eventos de auditoría.
Nota: autenticación vía sesión (login previo); sin paginación ni filtros en los endpoints API.

## Configuración DLP
- Crear/editar reglas y categorías vía admin o `seed_policies`.
- Parámetros globales en la primera fila de `PolicyConfig` (`severity_threshold`, `risk_score_threshold`, `store_extracted_text`). Si no existe fila, se usan valores por defecto (4, 20, False).

## Pruebas
- Ejecutar `pytest -v`. Incluye pruebas de carga/escaneo, generación de alertas y auditoría mediante API.

## Limitaciones conocidas
- Prototipo académico: sin aislamiento multi-tenant ni cifrado de archivos/texto.
- Escaneo síncrono; no hay colas ni antivirus.
- Enmascarado de hallazgos se aplica sólo en la UI; la API expone texto completo.
- Endpoints API sin paginación ni filtrado avanzado (excepto UI de alertas/auditoría).
- Almacenamiento local (`media/docs/`) y SQLite orientados a demo.

## Estructura breve
- `config/` ajustes y ruteo principal.
- `documents/` modelos de documentos, hallazgos y servicio de escaneo.
- `policies/` categorías, regex y config global; `management/commands/seed_policies.py`.
- `alerts/` alertas y permisos; lifecycle UI.
- `audit/` registro de eventos.
- `ui/` vistas, formularios, plantillas y `management/commands/seed_roles.py`.
