# Configuración Manual para Test Completo
# Este archivo muestra los pasos necesarios para completar la configuración

## 1. Agregar a INSTALLED_APPS (config/base.py)
```python
INSTALLED_APPS = [
    # ... otras apps
    'reg_test_completo',
]
```

## 2. Agregar URL (config/urls.py)
```python
urlpatterns = [
    # ... otras URLs
    path('reg_test_completo/', include('reg_test_completo.urls')),
]
```

## 3. Agregar al Menú (core/menu/menu_builder.py)
```python
menu = [
    # ... otros items
    MenuItem('Test Completo', 'reg_test_completo:list', 'fas fa-file-alt', module='registros'),
]
```

## 4. Crear Migraciones
```bash
python manage.py makemigrations reg_test_completo
python manage.py migrate
```

## 5. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
```

## 6. Verificar Funcionamiento
- Ir a http://localhost:8000/reg_test_completo/
- Verificar que aparezca en el menú lateral
- Probar crear un nuevo registro

## Notas
- La aplicación usa el sistema genérico de registros
- Los templates están en reg_test_completo/templates/reg_test_completo/
- La configuración está en reg_test_completo/config.py
- Los modelos heredan de RegistroBase y PasoBase
