from django.views.generic import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from core.utils.breadcrumbs import BreadcrumbsMixin
from registrostxtss.forms.registros0_form import Registros0Form
from core.models.sites import Site
from registrostxtss.models.main_registrostxtss import RegistrosTxTss
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework import status
from registrostxtss.models.r_sitio import Registros0
from registrostxtss.serializers.registros import Registros0Serializer

class CreateRegistroView(LoginRequiredMixin, BreadcrumbsMixin, FormView):
    template_name = 'pages/createReg.html'
    form_class = Registros0Form
    
    class Meta:
        title = 'Crear Registro Tx/Tss'
        header_title = 'Crear Registro Tx/Tss'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Obtener el registro_id de la URL
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            kwargs['registro_id'] = registro_id
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
            except RegistrosTxTss.DoesNotExist:
                context['error'] = 'Registro Tx/Tss no encontrado'
        
        return context
    
    def form_valid(self, form):
        # Guardar el formulario
        form.save()
        # Redirigir a la página de listado
        return redirect('registrostxtss:list')
    
    def form_invalid(self, form):
        print("form invalid")
        print(form.errors)
        # Si el formulario es inválido, volver a mostrar la página con errores
        return self.render_to_response(self.get_context_data(form=form))

# class Registros0ViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet para manejar las operaciones de Registros0
#     """
#     queryset = Registros0.objects.all()
#     serializer_class = Registros0Serializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [SearchFilter, OrderingFilter]
#     search_fields = ['sitio__name', 'sitio__pti_cell_id', 'sitio__operator_id']
#     ordering_fields = ['created_at', 'updated_at', 'sitio__name']
#     ordering = ['-created_at']

#     def perform_create(self, serializer):
#         """
#         Personalizar la creación del registro
#         """
#         serializer.save()

#     @action(detail=False, methods=['get'])
#     def por_sitio(self, request):
#         """
#         Endpoint para filtrar registros por sitio
#         """
#         sitio_id = request.query_params.get('sitio_id')
#         if sitio_id:
#             registros = self.queryset.filter(sitio_id=sitio_id)
#             serializer = self.get_serializer(registros, many=True)
#             return Response(serializer.data)
#         return Response({'error': 'sitio_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

