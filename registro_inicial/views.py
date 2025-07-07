from django.views.generic import TemplateView, CreateView, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from core.utils.breadcrumbs import BreadcrumbsMixin
from .models import RegistroInicial
from .forms import RegistroInicialForm

class RegistroInicialView(LoginRequiredMixin, BreadcrumbsMixin, ListView):
    model = RegistroInicial
    template_name = 'registro_inicial.html'
    context_object_name = 'registros'
    paginate_by = 10

    class Meta:
        title = 'Registros Iniciales'
        header_title = 'Registros Iniciales'


class NuevoRegistroView(LoginRequiredMixin, BreadcrumbsMixin, FormView):
    form_class = RegistroInicialForm
    template_name = 'nuevo_registro.html'
    success_url = reverse_lazy('registro_inicial:list')

    class Meta:
        title = 'Nuevo Registro'
        header_title = 'Nuevo Registro'

    def form_valid(self, form):
        # Aquí puedes procesar los datos del formulario sin guardar en modelo
        nombre = form.cleaned_data['nombre']
        fecha = form.cleaned_data['fecha']
        descripcion = form.cleaned_data['descripcion']
        
        # Aquí puedes hacer lo que necesites con los datos
        # Por ejemplo, guardar en otro lugar, enviar email, etc.
        
        messages.success(self.request, 'Registro procesado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor, corrija los errores en el formulario.')
        return super().form_invalid(form)


