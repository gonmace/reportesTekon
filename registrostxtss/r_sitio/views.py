from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils.breadcrumbs import BreadcrumbsMixin
from registrostxtss.r_sitio.form import RSitioForm
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from registrostxtss.r_sitio.models import RSitio
from django.shortcuts import get_object_or_404, redirect

class RSitioView(LoginRequiredMixin, BreadcrumbsMixin, FormView):
    template_name = 'pages/r_sitio.html'
    form_class = RSitioForm

    class Meta:
        title = 'Crear Registro Tx/Tss'
        header_title = 'Crear Registro Tx/Tss'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            kwargs['registro_id'] = registro_id
            # Verificar si ya existe un RSitio para este registro
            try:
                registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
                # Buscar si ya existe un RSitio para este registro
                rsitio_existente = RSitio.objects.filter(registro=registro_txtss).first()
                if rsitio_existente:
                    # Si existe, usar esa instancia para pre-llenar el formulario
                    kwargs['instance'] = rsitio_existente
            except RegistrosTxTss.DoesNotExist:
                pass
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        # Si se proporciona registro_id, usar ese registro
        if registro_id:
            try:
                registro_txtss = get_object_or_404(RegistrosTxTss, id=registro_id)
                sitio = registro_txtss.sitio
                context['sitio'] = sitio
                context['registro_txtss'] = registro_txtss
                
                # Verificar si ya existe un RSitio para este registro
                rsitio_existente = RSitio.objects.filter(registro=registro_txtss).first()
                if rsitio_existente:
                    context['is_editing'] = True
                    context['rsitio_existente'] = rsitio_existente
                else:
                    context['is_editing'] = False
                    
            except RegistrosTxTss.DoesNotExist:
                context['error'] = 'Registro Tx/Tss no encontrado'
        
        return context

    def form_valid(self, form):
        # Guardar el formulario
        form.save()
        # Redirigir a la página de listado
        return redirect('registrostxtss:steps', registro_id=form.instance.registro.id)

    def form_invalid(self, form):
        print("form invalid")
        print(form.errors)
        # Si el formulario es inválido, volver a mostrar la página con errores
        return self.render_to_response(self.get_context_data(form=form))

