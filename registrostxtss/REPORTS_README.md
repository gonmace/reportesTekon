# Sistema de Informes en PDF - Registros Tx/Tss

Este sistema permite generar informes en PDF de todos los registros vinculados a `RegistrosTxTss`, incluyendo información detallada de sitio, acceso y empalme.

## Características

- **Informe Completo**: Incluye todos los datos de cada registro con información detallada
- **Informe Resumido**: Estadísticas generales y resumen de completitud
- **Filtros Avanzados**: Por sitio, usuario, fecha y completitud
- **Interfaz Web**: Dashboard intuitivo para generar informes
- **Comando CLI**: Generación de informes desde línea de comandos
- **Personalización**: Múltiples opciones de filtrado y formato

## Instalación

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias necesarias ya están incluidas en `requirements.txt`:
- `reportlab==4.1.0` - Generación de PDFs
- `weasyprint==62.3` - Alternativa moderna para PDFs

### 2. Configuración

Asegúrate de que tu proyecto Django tenga configurado correctamente:
- `MEDIA_ROOT` para almacenar archivos generados
- `MEDIA_URL` para servir archivos estáticos

## Uso

### Interfaz Web

#### 1. Dashboard de Informes
Accede a: `/registrostxtss/reports/`

El dashboard muestra:
- Estadísticas generales del sistema
- Porcentajes de completitud por sección
- Botones para generar diferentes tipos de informes

#### 2. Lista de Registros con Filtros
Accede a: `/registrostxtss/reports/list/`

Características:
- Filtros por sitio, usuario, fecha y completitud
- Vista previa de registros antes de generar informe
- Generación de informes personalizados

#### 3. URLs Disponibles

```python
# Dashboard principal
/registrostxtss/reports/

# Lista con filtros
/registrostxtss/reports/list/

# Generar informes
/registrostxtss/reports/pdf/complete/     # Informe completo
/registrostxtss/reports/pdf/summary/      # Informe resumido
/registrostxtss/reports/pdf/custom/       # Informe personalizado (POST)
```

### Comando de Línea de Comandos

#### Sintaxis Básica

```bash
python manage.py generate_pdf_report [opciones]
```

#### Ejemplos de Uso

**1. Generar informe completo de todos los registros:**
```bash
python manage.py generate_pdf_report --tipo completo
```

**2. Generar informe resumido:**
```bash
python manage.py generate_pdf_report --tipo resumen
```

**3. Filtrar por sitio específico:**
```bash
python manage.py generate_pdf_report --sitio-id 1
```

**4. Filtrar por rango de fechas:**
```bash
python manage.py generate_pdf_report --fecha-inicio 2024-01-01 --fecha-fin 2024-12-31
```

**5. Filtrar solo registros completos:**
```bash
python manage.py generate_pdf_report --completitud completo
```

**6. Especificar archivo de salida:**
```bash
python manage.py generate_pdf_report --output /path/to/report.pdf
```

**7. Solo listar registros sin generar PDF:**
```bash
python manage.py generate_pdf_report --list-only
```

**8. Combinar múltiples filtros:**
```bash
python manage.py generate_pdf_report \
    --tipo completo \
    --sitio-id 1 \
    --user-id 5 \
    --fecha-inicio 2024-01-01 \
    --completitud completo \
    --output /tmp/informe_final.pdf
```

#### Opciones Disponibles

| Opción | Tipo | Descripción |
|--------|------|-------------|
| `--tipo` | completo/resumen | Tipo de informe a generar |
| `--output` | string | Ruta del archivo de salida |
| `--sitio-id` | int | ID del sitio para filtrar |
| `--user-id` | int | ID del usuario para filtrar |
| `--fecha-inicio` | YYYY-MM-DD | Fecha de inicio |
| `--fecha-fin` | YYYY-MM-DD | Fecha de fin |
| `--completitud` | completo/incompleto | Filtrar por completitud |
| `--list-only` | flag | Solo listar sin generar PDF |

## Estructura de los Informes

### Informe Completo

Cada registro incluye:

1. **Información Básica**
   - Sitio
   - Usuario
   - Fecha de creación
   - Estado

2. **Información de Sitio** (si existe)
   - Latitud y Longitud
   - Altura de Torre
   - Dimensiones
   - Deslindes
   - Comentarios

3. **Información de Acceso** (si existe)
   - Acceso al sitio
   - Acceso para construcción
   - Longitudes de acceso
   - Tipo de suelo
   - Obstáculos
   - Trabajos adicionales

4. **Información de Empalme** (si existe)
   - Latitud y Longitud del empalme
   - Proveedor de energía
   - Capacidad
   - Comentarios

### Informe Resumido

Incluye:

1. **Estadísticas Generales**
   - Total de registros
   - Registros con información de sitio
   - Registros con información de acceso
   - Registros con información de empalme
   - Porcentajes de completitud

2. **Lista de Registros**
   - Tabla con estado de completitud de cada registro
   - Indicadores visuales de completitud

## Personalización

### Modificar Estilos del PDF

Los estilos se pueden personalizar en `PDFReportService._setup_custom_styles()`:

```python
def _setup_custom_styles(self):
    # Personalizar colores, fuentes, tamaños, etc.
    self.styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=self.styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    ))
```

### Agregar Nuevos Campos

Para agregar nuevos campos a los informes:

1. Modificar el modelo correspondiente
2. Actualizar los métodos `_generate_*_section()` en `PDFReportService`
3. Actualizar las plantillas HTML si es necesario

## Solución de Problemas

### Error: "No module named 'reportlab'"
```bash
pip install reportlab
```

### Error: "Permission denied" al guardar archivo
Verificar permisos de escritura en el directorio de salida.

### Error: "MemoryError" con muchos registros
- Usar filtros para reducir el número de registros
- Considerar generar informes por lotes
- Aumentar la memoria disponible

### PDF muy grande
- Usar filtros para reducir registros
- Generar informes por períodos
- Considerar comprimir el PDF resultante

## Archivos Principales

- `services/pdf_report_service.py` - Lógica principal de generación de PDFs
- `views/reports.py` - Vistas para la interfaz web
- `templates/reports/` - Plantillas HTML
- `management/commands/generate_pdf_report.py` - Comando CLI
- `urls.py` - Configuración de URLs

## Contribución

Para agregar nuevas funcionalidades:

1. Crear tests para las nuevas características
2. Documentar los cambios
3. Actualizar este README
4. Verificar compatibilidad con versiones anteriores

## Licencia

Este sistema de informes es parte del proyecto Registros Tx/Tss y sigue las mismas condiciones de licencia. 