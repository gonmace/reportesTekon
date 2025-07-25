from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
import os
import re
from pathlib import Path


class Command(BaseCommand):
    help = 'Crea una nueva aplicación de registros completa con estructura similar a reg_txtss'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_name',
            type=str,
            help='Nombre de la aplicación (ej: reg_instalacion, reg_mantenimiento)'
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Título de la aplicación (ej: "Instalación", "Mantenimiento")'
        )
        parser.add_argument(
            '--description',
            type=str,
            help='Descripción de la aplicación'
        )
        parser.add_argument(
            '--pasos',
            nargs='+',
            default=['paso1', 'paso2', 'paso3'],
            help='Lista de pasos para el registro (ej: sitio acceso empalme)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la creación aunque la aplicación ya exista'
        )

    def handle(self, *args, **options):
        app_name = options['app_name']
        title = options['title'] or app_name.replace('reg_', '').title()
        description = options['description'] or f'Aplicación para registros de {title.lower()}'
        pasos = options['pasos']
        force = options['force']

        # Validar nombre de aplicación
        if not re.match(r'^[a-z][a-z0-9_]*$', app_name):
            raise CommandError('El nombre de la aplicación debe ser en minúsculas y solo puede contener letras, números y guiones bajos')

        # Verificar si la aplicación ya existe
        app_path = Path(settings.BASE_DIR) / app_name
        if app_path.exists() and not force:
            raise CommandError(f'La aplicación "{app_name}" ya existe. Usa --force para sobrescribir.')

        self.stdout.write(f'Creando aplicación "{app_name}"...')

        # Crear la aplicación Django manualmente
        if app_path.exists() and not force:
            raise CommandError(f'La aplicación "{app_name}" ya existe. Usa --force para sobrescribir.')
        
        if app_path.exists() and force:
            import shutil
            shutil.rmtree(app_path)
        
        # Crear estructura de directorios
        app_path.mkdir(exist_ok=True)
        (app_path / 'migrations').mkdir(exist_ok=True)
        (app_path / 'templates').mkdir(exist_ok=True)
        (app_path / 'templates' / app_name).mkdir(exist_ok=True)
        (app_path / 'templates' / app_name / 'partials').mkdir(exist_ok=True)
        
        # Crear archivos __init__.py
        (app_path / '__init__.py').touch()
        (app_path / 'migrations' / '__init__.py').touch()

        # Crear estructura de archivos
        self._create_app_structure(app_name, title, description, pasos)
        
        # Crear templates
        self._create_templates(app_name, title, pasos)
        
        # Crear archivos de configuración
        self._create_config_files(app_name, title, pasos)
        
        # Crear archivos de vistas
        self._create_views(app_name, title, pasos)
        
        # Crear archivos de formularios
        self._create_forms(app_name, pasos)
        
        # Crear archivos de modelos
        self._create_models(app_name, title, pasos)
        
        # Crear archivos de admin
        self._create_admin(app_name, pasos)
        
        # Crear archivos de URLs
        self._create_urls(app_name, title)
        
                # Crear archivos de apps.py
        self._create_apps_py(app_name, title, description)
        
        # Crear archivo de configuración de ejemplo
        self._create_setup_example(app_name, title)

        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Aplicación "{app_name}" creada exitosamente!\n'
                f'✓ Título: {title}\n'
                f'✓ Pasos: {", ".join(pasos)}\n'
                f'✓ No olvides completar la configuración manual:'
            )
        )
        
        # Mostrar pasos de configuración manual
        self.stdout.write(
            self.style.WARNING(
                '\n📋 PASOS DE CONFIGURACIÓN MANUAL:\n'
                '1. Agregar "{app_name}" a INSTALLED_APPS en config/base.py\n'
                '2. Agregar URL en config/urls.py: path("{app_name}/", include("{app_name}.urls"))\n'
                '3. Agregar al menú en core/menu/menu_builder.py\n'
                '4. Ejecutar: python manage.py makemigrations {app_name}\n'
                '5. Ejecutar: python manage.py migrate\n'
                '6. Crear superusuario si no existe: python manage.py createsuperuser\n'
            )
        )

    def _create_app_structure(self, app_name, title, description, pasos):
        """Crear estructura de directorios y archivos base"""
        app_path = Path(settings.BASE_DIR) / app_name
        
        # Crear directorios adicionales
        (app_path / 'templates' / app_name).mkdir(parents=True, exist_ok=True)
        (app_path / 'templates' / app_name / 'partials').mkdir(parents=True, exist_ok=True)

    def _create_templates(self, app_name, title, pasos):
        """Crear templates HTML"""
        app_path = Path(settings.BASE_DIR) / app_name
        templates_path = app_path / 'templates' / app_name

        # Template principal de listado
        list_template = f'''{{% extends "base.html" %}}
{{% load static %}}

{{% block title %}}{title}{{% endblock %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">{title}</h1>
        <a href="{{% url '{app_name}:create' %}}" class="btn btn-primary">
            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Nuevo Registro
        </a>
    </div>

    <div class="bg-white shadow-md rounded-lg overflow-hidden">
        <div class="p-6">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                ID
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Título
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Sitio
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Usuario
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Fecha
                            </th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Acciones
                            </th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        {{% for registro in registros %}}
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                {{%{{ registro.id %}}%}}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {{%{{ registro.title %}}%}}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{%{{ registro.sitio.name|default:"Sin sitio" %}}%}}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{%{{ registro.user.username|default:"Sin usuario" %}}%}}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                {{%{{ registro.created_at|date:"d/m/Y" %}}%}}
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <a href="{{% url '{app_name}:steps' registro.id %}}" class="text-indigo-600 hover:text-indigo-900">
                                    Ver Pasos
                                </a>
                            </td>
                        </tr>
                        {{% endfor %}}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{{% endblock %}}'''

        with open(templates_path / 'list.html', 'w', encoding='utf-8') as f:
            f.write(list_template)

        # Template de pasos
        steps_template = f'''{{% extends "base.html" %}}
{{% load static %}}

{{% block title %}}{title} - Pasos{{% endblock %}}

{{% block content %}}
<div class="container mx-auto px-4 py-8">
    <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">{title}</h1>
        <p class="text-gray-600">Registro #{{%{{ registro.id %}}%}}</p>
    </div>

    <div class="bg-white shadow-md rounded-lg overflow-hidden">
        <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8 px-6">
                {{% for paso in pasos %}}
                <a href="?paso={{%{{ paso.nombre %}}%}}" 
                   class="py-4 px-1 border-b-2 font-medium text-sm {{% if paso.activo %}}border-indigo-500 text-indigo-600{{% else %}}border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300{{% endif %}}">
                    {{%{{ paso.titulo %}}%}}
                </a>
                {{% endfor %}}
            </nav>
        </div>

        <div class="p-6">
            {{% block paso_content %}}
            <p class="text-gray-500">Selecciona un paso para comenzar.</p>
            {{% endblock %}}
        </div>
    </div>
</div>
{{% endblock %}}'''

        with open(templates_path / 'steps.html', 'w', encoding='utf-8') as f:
            f.write(steps_template)

    def _create_config_files(self, app_name, title, pasos):
        """Crear archivos de configuración"""
        app_path = Path(settings.BASE_DIR) / app_name

        # Configuración principal
        config_content = f'''"""
Configuración declarativa para registros {title}.
"""

from registros.config import (
    create_simple_config, 
    create_registro_config,
    create_1_point_map_config,
    create_2_point_map_config,
    create_3_point_map_config,
    create_photos_config,
    create_custom_config,
    create_sub_element_only_config
)
from .models import {app_name.title().replace('_', '')}, {', '.join([paso.title() for paso in pasos])}
from .forms import {', '.join([f'{paso.title()}Form' for paso in pasos])}
from core.models.sites import Site

# Configuración de pasos
PASOS_CONFIG = {{'''

        for i, paso in enumerate(pasos):
            config_content += f'''
    '{paso}': create_custom_config(
        model_class={paso.title()},
        form_class={paso.title()}Form,
        title='{paso.title()}',
        description='Información sobre {paso.lower()}.',
        template_form='components/elemento_form.html'
    ),'''

        config_content += f'''
}}

# Configuración completa del registro
REGISTRO_CONFIG = create_registro_config(
    registro_model={app_name.title().replace('_', '')},
    pasos_config=PASOS_CONFIG,
    title='{title}',
    app_namespace='{app_name}',
    list_template='{app_name}/list.html',
    steps_template='{app_name}/steps.html'
)'''

        with open(app_path / 'config.py', 'w', encoding='utf-8') as f:
            f.write(config_content)

    def _create_views(self, app_name, title, pasos):
        """Crear archivos de vistas"""
        app_path = Path(settings.BASE_DIR) / app_name

        views_content = f'''"""
Vistas para registros {title}.
"""

from registros.views.generic_registro_views import (
    GenericRegistroTableListView, 
    GenericRegistroStepsView, 
    GenericElementoView
)
from registros.views.generic_views import GenericActivarRegistroView
from .config import REGISTRO_CONFIG
from django.urls import reverse
from django.shortcuts import get_object_or_404


class ListRegistrosView(GenericRegistroTableListView):
    """Vista para listar registros {title} usando tabla genérica."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs para la página de listado."""
        return [
            {{'label': 'Inicio', 'url': reverse('dashboard:dashboard')}},
            {{'label': '{title}'}}  # Página actual sin URL
        ]


class StepsRegistroView(GenericRegistroStepsView):
    """Vista para mostrar los pasos de un registro {title}."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto y establece el registro."""
        registro_id = self.kwargs.get('registro_id')
        self.registro = get_object_or_404(self.registro_config.registro_model, id=registro_id)
        context = super().get_context_data(**kwargs)
        return context
    
    def get_header_title(self):
        """Obtiene el título del header basado en PTI ID o Operador ID."""
        if hasattr(self, 'registro') and self.registro:
            # Intentar obtener PTI ID primero
            pti_id = getattr(getattr(self.registro, 'sitio', None), 'pti_cell_id', None)
            if pti_id:
                return pti_id
            
            # Si no hay PTI ID, intentar Operador ID
            operador_id = getattr(getattr(self.registro, 'sitio', None), 'operator_id', None)
            if operador_id:
                return operador_id
        
        return super().get_header_title()


class ElementoRegistroView(GenericElementoView):
    """Vista para manejar elementos de registro {title}."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG
    
    def get(self, request, registro_id, paso_nombre):
        """Establece el registro antes de procesar la petición."""
        self.registro = self.registro_config.registro_model.objects.get(id=registro_id)
        return super().get(request, registro_id, paso_nombre)
    
    def get_header_title(self):
        """Obtiene el título del header basado en el nombre del sitio."""
        if hasattr(self, 'registro') and self.registro:
            name = getattr(getattr(self.registro, 'sitio', None), 'name', 'Sin PTI')
            return name
        return super().get_header_title()


class ActivarRegistroView(GenericActivarRegistroView):
    """Vista para activar registros {title}."""
    
    def get_registro_config(self):
        return REGISTRO_CONFIG'''

        with open(app_path / 'views.py', 'w', encoding='utf-8') as f:
            f.write(views_content)

    def _create_forms(self, app_name, pasos):
        """Crear archivos de formularios"""
        app_path = Path(settings.BASE_DIR) / app_name

        forms_content = f'''"""
Formularios para registros {app_name}.
"""

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Div
from .models import {app_name.title().replace('_', '')}, {', '.join([paso.title() for paso in pasos])}
from registros.forms.utils import get_form_field_css_class

'''

        for paso in pasos:
            forms_content += f'''
class {paso.title()}Form(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.registro_id = kwargs.pop('registro_id', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = ''
        self.helper.form_class = 'p-0 md:p-2'
        self.helper.label_class = 'text-sm text-base-content'
        self.helper.field_class = 'mb-2'
        
        # Configurar el campo registro automáticamente
        self.fields['registro'].queryset = {app_name.title().replace('_', '')}.objects.all()
        
        try:
            if self.registro_id:
                registro_obj = {app_name.title().replace('_', '')}.objects.get(id=self.registro_id)
                self.fields['registro'].widget = forms.HiddenInput()
                self.initial['registro'] = registro_obj.id
                self.fields['registro'].initial = registro_obj.id
            elif self.instance.pk:
                self.fields['registro'].widget = forms.HiddenInput()
            else:
                self.fields['registro'].widget = forms.HiddenInput()
        except {app_name.title().replace('_', '')}.DoesNotExist:
            self.fields['registro'].widget = forms.HiddenInput()

        self.helper.layout = Layout(
            Field('registro'),
            Field('comentarios', css_class=f"{{get_form_field_css_class(self, 'comentarios')}} w-full"),
            Div(
                Submit('submit', 'Guardar Registro', css_class='btn btn-success w-full mt-4 sombra'),
                css_class='text-center'
            ),
        )
    
    class Meta:
        model = {paso.title()}
        fields = ['registro', 'comentarios']
        labels = {{
            'comentarios': 'Comentarios',
        }}
        widgets = {{
            'comentarios': forms.Textarea(attrs={{'rows': 4, 'placeholder': 'Ingrese comentarios...'}}),
        }}

'''

        with open(app_path / 'forms.py', 'w', encoding='utf-8') as f:
            f.write(forms_content)

    def _create_models(self, app_name, title, pasos):
        """Crear archivos de modelos"""
        app_path = Path(settings.BASE_DIR) / app_name

        models_content = f'''"""
Modelos para registros {title}.
"""

from registros.models.base import RegistroBase
from registros.models.paso import PasoBase
from django.db import models
from registros.models.validators import validar_latitud, validar_longitud
from registros.models.completeness_checker import check_model_completeness
from core.models.sites import Site
from users.models import User
from simple_history.models import HistoricalRecords

class {app_name.title().replace('_', '')}(RegistroBase):
    """
    Modelo para registros {title}.
    """
    sitio = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Sitio', related_name='{app_name}')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Usuario', related_name='{app_name}')
    title = models.CharField(max_length=100, verbose_name='Título')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{app_name.title().replace('_', '')} {{self.id}}"
    
    def clean(self):
        """Custom validation method"""
        super().clean()
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs) 

'''

        for paso in pasos:
            models_content += f'''
class {paso.title()}(PasoBase):
    """Paso {paso.title()} para registros {title}."""
    registro = models.ForeignKey({app_name.title().replace('_', '')}, on_delete=models.CASCADE, verbose_name='Registro')
    comentarios = models.TextField(blank=True, null=True, verbose_name='Comentarios')
    
    class Meta:
        verbose_name = 'Registro {paso.title()}'
        verbose_name_plural = 'Registros {paso.title()}'
    
    @staticmethod
    def get_etapa():
        return '{paso}'
    
    @staticmethod
    def get_actives():
        return {paso.title()}.objects.filter(is_deleted=False)

    @staticmethod
    def check_completeness({paso}_id):
        return check_model_completeness({paso.title()}, {paso}_id)

'''

        with open(app_path / 'models.py', 'w', encoding='utf-8') as f:
            f.write(models_content)

    def _create_admin(self, app_name, pasos):
        """Crear archivos de admin"""
        app_path = Path(settings.BASE_DIR) / app_name

        admin_content = f'''"""
Admin para registros {app_name}.
"""

from django.contrib import admin
from .models import {app_name.title().replace('_', '')}, {', '.join([paso.title() for paso in pasos])}

@admin.register({app_name.title().replace('_', '')})
class {app_name.title().replace('_', '')}Admin(admin.ModelAdmin):
    list_display = ['id', 'title', 'sitio', 'user', 'created_at']
    list_filter = ['created_at', 'sitio']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

'''

        for paso in pasos:
            admin_content += f'''
@admin.register({paso.title()})
class {paso.title()}Admin(admin.ModelAdmin):
    list_display = ['id', 'registro', 'created_at']
    list_filter = ['created_at']
    search_fields = ['comentarios']
    readonly_fields = ['created_at', 'updated_at']

'''

        with open(app_path / 'admin.py', 'w', encoding='utf-8') as f:
            f.write(admin_content)

    def _create_urls(self, app_name, title):
        """Crear archivos de URLs"""
        app_path = Path(settings.BASE_DIR) / app_name

        urls_content = f'''"""
URLs para registros {title}.
"""

from django.urls import path
from .views import ListRegistrosView, StepsRegistroView, ElementoRegistroView, ActivarRegistroView

app_name = '{app_name}'

urlpatterns = [
    path('', ListRegistrosView.as_view(), name='list'),
    path('<int:registro_id>/steps/', StepsRegistroView.as_view(), name='steps'),
    path('<int:registro_id>/<str:paso_nombre>/', ElementoRegistroView.as_view(), name='elemento'),
    path('<int:registro_id>/activar/', ActivarRegistroView.as_view(), name='activar'),
]'''

        with open(app_path / 'urls.py', 'w', encoding='utf-8') as f:
            f.write(urls_content)

    def _create_apps_py(self, app_name, title, description):
        """Crear archivo apps.py"""
        app_path = Path(settings.BASE_DIR) / app_name

        apps_content = f'''"""
Configuración de la aplicación {title}.
"""

from django.apps import AppConfig


class {app_name.title().replace('_', '')}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{title}'
    description = '{description}'
'''

        with open(app_path / 'apps.py', 'w', encoding='utf-8') as f:
            f.write(apps_content)

    def _create_setup_example(self, app_name, title):
        """Crear archivo de ejemplo de configuración"""
        app_path = Path(settings.BASE_DIR) / app_name
        
        setup_content = f'''# Configuración Manual para {title}
# Este archivo muestra los pasos necesarios para completar la configuración

## 1. Agregar a INSTALLED_APPS (config/base.py)
```python
INSTALLED_APPS = [
    # ... otras apps
    '{app_name}',
]
```

## 2. Agregar URL (config/urls.py)
```python
urlpatterns = [
    # ... otras URLs
    path('{app_name}/', include('{app_name}.urls')),
]
```

## 3. Agregar al Menú (core/menu/menu_builder.py)
```python
menu = [
    # ... otros items
    MenuItem('{title}', '{app_name}:list', 'fas fa-file-alt', module='registros'),
]
```

## 4. Crear Migraciones
```bash
python manage.py makemigrations {app_name}
python manage.py migrate
```

## 5. Crear Superusuario (si no existe)
```bash
python manage.py createsuperuser
```

## 6. Verificar Funcionamiento
- Ir a http://localhost:8000/{app_name}/
- Verificar que aparezca en el menú lateral
- Probar crear un nuevo registro

## Notas
- La aplicación usa el sistema genérico de registros
- Los templates están en {app_name}/templates/{app_name}/
- La configuración está en {app_name}/config.py
- Los modelos heredan de RegistroBase y PasoBase
'''
        
        with open(app_path / 'SETUP.md', 'w', encoding='utf-8') as f:
            f.write(setup_content) 