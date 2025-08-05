# Configuración Manual para Reporte de construcción
# Este archivo muestra los pasos necesarios para completar la configuración

## 1. Agregar a INSTALLED_APPS (config/base.py)
```python
INSTALLED_APPS = [
    # ... otras apps
    'reg_construccion',
]
```

## 2. Agregar URL (config/urls.py)
```python
urlpatterns = [
    # ... otras URLs
    path('reg_construccion/', include('reg_construccion.urls')),
]
```

## 3. Agregar al Menú (core/menu/menu_builder.py)
```python
menu = [
    # ... otros items
    MenuItem('Reporte de construcción', 'reg_construccion:list', 'fas fa-file-alt', module='registros'),
]
```

## 4. Crear Migraciones
```bash
python manage.py makemigrations reg_construccion
python manage.py migrate
```

## 5. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
```

## 6. Verificar Funcionamiento
- Ir a http://localhost:8000/reg_construccion/
- Verificar que aparezca en el menú lateral
- Probar crear un nuevo registro

## 7. Generar PDF (Opcional)
- Ir a http://localhost:8000/reg_construccion/pdf/1/ para generar PDF
- Ir a http://localhost:8000/reg_construccion/preview/1/ para previsualizar

## Notas
- La aplicación usa el sistema genérico de registros
- Los templates están en reg_construccion/templates/reg_construccion/
- La configuración está en reg_construccion/config.py
- Los modelos heredan de RegistroBase y PasoBase
- **PDF automático**: Se generan templates y vistas de PDF automáticamente
- **Templates PDF**: En pdf_reports/templates/reportes_reg_construccion/
- **Vista PDF**: reg_construccion/pdf_views.py
