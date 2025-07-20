from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from registros_txtss.models import Registros
from core.utils.breadcrumbs import BreadcrumbsMixin

class GenericRegistroView(LoginRequiredMixin, BreadcrumbsMixin, FormView):
    """
    Vista genérica para manejar cualquier modelo de registro.
    Cada modelo debe tener su propio formulario específico.
    """
    template_name = 'pages/generic_registro.html'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_class = None
        self.etapa = None
    
    def setup(self, request, *args, **kwargs):
        """Configura la vista con el modelo específico."""
        super().setup(request, *args, **kwargs)
        
        # Obtener el modelo y etapa de los kwargs
        self.model_class = kwargs.get('model_class')
        self.etapa = kwargs.get('etapa', 'registro')
        
        if not self.model_class:
            raise ValueError("model_class debe ser especificado")
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            kwargs['registro_id'] = registro_id
            # Verificar si ya existe un registro para este registro_txtss
            try:
                registro_txtss = get_object_or_404(Registros, id=registro_id)
                registro_existente = self.model_class.objects.filter(registro=registro_txtss).first()
                if registro_existente:
                    kwargs['instance'] = registro_existente
            except Registros.DoesNotExist:
                pass
        return kwargs
    
    def get_page_title(self):
        """Genera el título de la página basado en la etapa y el sitio"""
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        sitio_name = "Registro"
        
        if registro_id:
            try:
                registro_txtss = get_object_or_404(Registros, id=registro_id)
                
                try:
                    pti_id = registro_txtss.sitio.pti_cell_id
                    operator_id = registro_txtss.sitio.operator_id
                    sitio_name = f"{pti_id} / {operator_id}"
                except AttributeError:
                    try:
                        sitio_name = registro_txtss.sitio.pti_cell_id
                    except AttributeError:
                        sitio_name = registro_txtss.sitio.operator_id
                
            except Registros.DoesNotExist:
                sitio_name = "Registro"
        return f"{sitio_name}"
    
    def get_breadcrumbs(self):
        """Genera breadcrumbs dinámicos basados en la etapa y registro_id"""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
            {'label': 'Registros TX/TSS', 'url_name': 'registros_txtss:list'}
        ]
        
        # Obtener el nombre del sitio del registro
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            try:
                registro_txtss = get_object_or_404(Registros, id=registro_id)
                try:
                    sitio_cod = registro_txtss.sitio.pti_cell_id
                    
                    breadcrumbs.append({
                        'label': sitio_cod, 
                        'url_name': 'registros_txtss:steps',
                        'url_kwargs': {'registro_id': registro_id}
                    })
                except AttributeError:
                    sitio_cod = registro_txtss.sitio.operator_id
                    breadcrumbs.append({
                        'label': sitio_cod, 
                        'url_name': 'registros_txtss:steps',
                        'url_kwargs': {'registro_id': registro_id}
                    })

            except Registros.DoesNotExist:
                breadcrumbs.append({'label': 'Registro'})
        else:
            breadcrumbs.append({'label': 'Registro'})
        
        # Agregar la etapa actual
        if self.etapa:
            breadcrumbs.append({'label': self.etapa.title()})
        
        return self._resolve_breadcrumbs(breadcrumbs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['etapa'] = self.etapa
        context['model_name'] = self.model_class.__name__
        
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            try:
                registro_txtss = get_object_or_404(Registros, id=registro_id)
                sitio = registro_txtss.sitio
                context['sitio'] = sitio
                context['registro_txtss'] = registro_txtss
                
                # Verificar si ya existe un registro para este registro_txtss
                registro_existente = self.model_class.objects.filter(registro=registro_txtss).first()
                if registro_existente:
                    context['is_editing'] = True
                    context['registro_existente'] = registro_existente
                else:
                    context['is_editing'] = False
                    
            except Registros.DoesNotExist:
                context['error'] = 'Registro no encontrado'
        
        return context
    
    def form_valid(self, form):
        # Guardar el formulario
        form.save()
        # Redirigir a la página de listado
        return redirect('registros_txtss:steps', registro_id=form.instance.registro.id)
    
    def form_invalid(self, form):
        print("form invalid")
        print(form.errors)
        # Si el formulario es inválido, volver a mostrar la página con errores
        return self.render_to_response(self.get_context_data(form=form)) 