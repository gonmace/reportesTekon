# Configuración Manual para Reporte de visita
# Este archivo muestra los pasos necesarios para completar la configuración

## 1. Agregar a INSTALLED_APPS (config/base.py)
```python
INSTALLED_APPS = [
    # ... otras apps
    'reg_visita',
]
```

## 2. Agregar URL (config/urls.py)
```python
urlpatterns = [
    # ... otras URLs
    path('reg_visita/', include('reg_visita.urls')),
]
```

## 3. Agregar al Menú (core/menu/menu_builder.py)
```python
menu = [
    # ... otros items
    MenuItem('Reporte de visita', 'reg_visita:list', 'fas fa-file-alt', module='registros'),
]
```

## 4. Crear Migraciones
```bash
python manage.py makemigrations reg_visita
python manage.py migrate
```

## 5. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
```

## 6. Verificar Funcionamiento
- Ir a http://localhost:8000/reg_visita/
- Verificar que aparezca en el menú lateral
- Probar crear un nuevo registro

## 7. Generar PDF (Opcional)
- Ir a http://localhost:8000/reg_visita/pdf/1/ para generar PDF
- Ir a http://localhost:8000/reg_visita/preview/1/ para previsualizar

## Notas
- La aplicación usa el sistema genérico de registros
- Los templates están en reg_visita/templates/reg_visita/
- La configuración está en reg_visita/config.py
- Los modelos heredan de RegistroBase y PasoBase
- **PDF automático**: Se generan templates y vistas de PDF automáticamente
- **Templates PDF**: En pdf_reports/templates/reportes_reg_visita/
- **Vista PDF**: reg_visita/pdf_views.py
