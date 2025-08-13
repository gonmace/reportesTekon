# Sistema de Reportes de Construcción

## Descripción General

El sistema de reportes de construcción es una aplicación fullstack de Django que permite gestionar y generar reportes detallados del progreso de construcción de proyectos. El sistema incluye funcionalidades para:

- Crear y gestionar reportes de construcción
- Registrar avances por componente
- Generar reportes en PDF
- Dashboard con estadísticas
- Interfaz moderna con DaisyUI

## Características Principales

### 🏗️ Gestión de Reportes
- **CRUD completo** de reportes de construcción
- **Asociación con sitios** y estructuras de proyecto
- **Sistema de pasos** para completar reportes
- **Historial de cambios** con django-simple-history

### 📊 Avances por Componente
- **Registro de porcentajes** actual y acumulado
- **Validaciones automáticas** de porcentajes
- **Cálculo de ejecución** por componente
- **Comentarios detallados** por avance

### 🎨 Interfaz Moderna
- **Diseño responsivo** con DaisyUI
- **Componentes interactivos** con JavaScript
- **Búsqueda y filtros** avanzados
- **Acciones en lote** para múltiples registros

### 📈 Dashboard y Estadísticas
- **Métricas en tiempo real** de reportes
- **Gráficos de progreso** por componente
- **Resumen de actividades** recientes
- **Indicadores de estado** visuales

## Estructura del Proyecto

```
reg_construccion/
├── models.py              # Modelos de datos
├── views.py               # Vistas y lógica de negocio
├── forms.py               # Formularios con DaisyUI
├── admin.py               # Configuración del admin
├── urls.py                # Rutas de la aplicación
├── config.py              # Configuración de pasos
├── pdf_views.py           # Generación de PDFs
├── templates/             # Plantillas HTML
│   └── reg_construccion/
│       ├── list.html      # Lista de reportes
│       ├── dashboard.html # Dashboard principal
│       ├── registro_form.html
│       └── registro_confirm_delete.html
└── management/            # Comandos personalizados
```

## Modelos de Datos

### RegConstruccion
Modelo principal que representa un reporte de construcción.

```python
class RegConstruccion(RegistroBase):
    sitio = models.ForeignKey(Site, ...)
    user = models.ForeignKey(User, ...)
    estructura = models.ForeignKey(GrupoComponentes, ...)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
```

### AvanceComponente
Registra el progreso de cada componente de la estructura.

```python
class AvanceComponente(PasoBase):
    registro = models.ForeignKey(RegConstruccion, ...)
    fecha = models.DateField(default=date.today)
    componente = models.ForeignKey(Componente, ...)
    porcentaje_actual = models.IntegerField(default=0)
    porcentaje_acumulado = models.IntegerField(default=0)
    comentarios = models.TextField(blank=True, null=True)
```

### Objetivo y Comentarios
Modelos para almacenar información adicional del reporte.

## Funcionalidades Principales

### 1. Creación de Reportes

```python
# Vista para crear nuevos reportes
class RegConstruccionCreateView(LoginRequiredMixin, CreateView):
    model = RegConstruccion
    form_class = RegConstruccionForm
    template_name = 'reg_construccion/registro_form.html'
```

**Características:**
- Formulario con validación en tiempo real
- Selección de sitio y estructura
- Campos con estilos de DaisyUI
- Redirección automática a pasos

### 2. Sistema de Pasos

El sistema utiliza un framework de pasos genérico que permite:

- **Objetivo**: Definir el propósito del reporte
- **Avance por Componente**: Registrar progreso detallado
- **Imágenes**: Adjuntar fotografías del avance

### 3. Dashboard Interactivo

```python
@login_required
def dashboard_construccion(request):
    # Estadísticas en tiempo real
    total_registros = RegConstruccion.objects.filter(user=request.user).count()
    registros_hoy = RegConstruccion.objects.filter(
        user=request.user,
        created_at__date=date.today()
    ).count()
```

**Características:**
- Métricas visuales con cards de DaisyUI
- Lista de reportes recientes
- Componentes más activos
- Acciones rápidas

### 4. Gestión de Avances

```python
@login_required
@require_POST
def guardar_ejecucion(request, registro_id):
    # Actualización masiva de porcentajes
    for key, value in request.POST.items():
        if key.startswith('ejec_actual_'):
            componente_id = key.split('_')[2]
            nuevo_valor = int(value) if value else 0
            # Validación y guardado
```

**Características:**
- Actualización AJAX en tiempo real
- Validación de porcentajes (0-100)
- Cálculo automático de acumulados
- Historial de cambios

## Interfaz de Usuario

### Diseño con DaisyUI

El sistema utiliza DaisyUI para una interfaz moderna y consistente:

```html
<!-- Ejemplo de card con estadísticas -->
<div class="stat bg-base-100 shadow-xl rounded-lg">
    <div class="stat-figure text-primary">
        <svg class="w-8 h-8">...</svg>
    </div>
    <div class="stat-title">Total Reportes</div>
    <div class="stat-value text-primary">{{ total_registros }}</div>
    <div class="stat-desc">Reportes de construcción creados</div>
</div>
```

### Componentes Interactivos

- **Tablas con ordenamiento** y filtros
- **Dropdowns** para acciones
- **Modales** de confirmación
- **Formularios** con validación
- **Búsqueda** en tiempo real

### Responsive Design

- **Mobile-first** approach
- **Grid system** adaptativo
- **Componentes flexibles**
- **Navegación optimizada**

## Configuración

### Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar base de datos:**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Crear superusuario:**
```bash
python manage.py createsuperuser
```

### Configuración de Pasos

El sistema utiliza una configuración declarativa en `config.py`:

```python
PASOS_CONFIG = {
    'objetivo': create_custom_config(
        model_class=Objetivo,
        form_class=ObjetivoForm,
        title='Objetivo',
        description='Objetivo del registro de construcción.',
        template_form='components/elemento_form.html'
    ),
    'avance_componente': create_custom_config(
        model_class=AvanceComponenteComentarios,
        form_class=AvanceComponenteComentariosForm,
        title='Avance',
        description='Tabla de avances por componente de la estructura.',
        template_form='components/elemento_form.html',
        sub_elementos=[table_avance_componente]
    ),
    # ...
}
```

## URLs Principales

```python
urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('dashboard/', dashboard_construccion, name='dashboard'),
    path('crear/', RegConstruccionCreateView.as_view(), name='create'),
    path('<int:registro_id>/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/editar/', RegConstruccionUpdateView.as_view(), name='update'),
    path('<int:registro_id>/eliminar/', RegConstruccionDeleteView.as_view(), name='delete'),
    path('pdf/<int:registro_id>/', RegConstruccionPDFView.as_view(), name='pdf'),
]
```

## Uso del Sistema

### 1. Crear un Reporte

1. Navegar a "Nuevo Reporte"
2. Seleccionar sitio y estructura
3. Completar título y descripción
4. Guardar y continuar con los pasos

### 2. Completar Pasos

1. **Objetivo**: Definir el propósito del reporte
2. **Avance**: Registrar porcentajes por componente
3. **Imágenes**: Adjuntar fotografías del progreso

### 3. Gestionar Reportes

- **Lista**: Ver todos los reportes con filtros
- **Dashboard**: Estadísticas y resumen
- **Editar**: Modificar información existente
- **Eliminar**: Remover reportes (con confirmación)

### 4. Generar PDFs

- Acceder desde la lista de reportes
- Descargar reporte completo en PDF
- Incluye todos los datos y avances

## Características Técnicas

### Seguridad
- **Autenticación requerida** para todas las vistas
- **Validación de permisos** por usuario
- **CSRF protection** en formularios
- **Sanitización** de datos de entrada

### Performance
- **Optimización de queries** con select_related
- **Paginación** en listas grandes
- **Caché** de estadísticas
- **Lazy loading** de componentes

### Mantenibilidad
- **Código modular** y reutilizable
- **Configuración declarativa** de pasos
- **Documentación** completa
- **Tests unitarios** (recomendado)

## Extensibilidad

El sistema está diseñado para ser fácilmente extensible:

### Agregar Nuevos Pasos

1. Crear modelo en `models.py`
2. Crear formulario en `forms.py`
3. Agregar configuración en `config.py`
4. Crear plantilla en `templates/`

### Personalizar Estilos

- Modificar clases de DaisyUI
- Agregar CSS personalizado
- Crear componentes reutilizables

### Integrar con Otros Sistemas

- **APIs REST** para integración externa
- **Webhooks** para notificaciones
- **Exportación** a otros formatos

## Contribución

Para contribuir al proyecto:

1. **Fork** el repositorio
2. **Crear** rama para feature
3. **Implementar** cambios
4. **Agregar** tests
5. **Documentar** cambios
6. **Crear** pull request

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## Soporte

Para soporte técnico o preguntas:

- **Issues**: Crear issue en GitHub
- **Documentación**: Revisar este README
- **Email**: Contactar al equipo de desarrollo

---

**Desarrollado con ❤️ usando Django y DaisyUI**


