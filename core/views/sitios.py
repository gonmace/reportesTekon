from django.views.generic import TemplateView
from rest_framework import viewsets
from core.models.sites import Site
from core.serializers import SiteSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from core.utils.breadcrumbs import BreadcrumbsMixin
from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from core.forms import SiteForm
from django.template.loader import render_to_string
import json

# views.py
class SitiosView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    template_name = 'pages/sitios.html'
    context_object_name = 'sitios'

    class Meta:
        title = 'Sitios'
        header_title = 'Registro de Sitios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_superuser'] = self.request.user.is_superuser
        return context

class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    
    def get_queryset(self):
        return Site.objects.filter(is_deleted=False)

    def update(self, request, *args, **kwargs):
        """Actualizar sitio, incluyendo soft delete."""
        instance = self.get_object()
        
        # Verificar si solo se está modificando is_deleted
        only_is_deleted = len(request.data) == 1 and 'is_deleted' in request.data
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        if only_is_deleted:
            message = 'Registro eliminado'
        else:
            message = f'Sitio "{instance.name}" actualizado correctamente.'
            
        return Response({'success': True, 'message': message}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Soft delete: marcar is_deleted=True en lugar de eliminar."""
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response({'success': True, 'message': f'Sitio "{instance.name}" eliminado correctamente.'}, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class SiteEditModalView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, site_id):
        site = get_object_or_404(Site, id=site_id)
        form = SiteForm(instance=site)
        
        # Renderizar el formulario usando Crispy Forms
        form_html = render_to_string('sites/update_site_form.html', {
            'form': form,
            'site': site
        }, request=request)
        
        return JsonResponse({
            'success': True,
            'form_html': form_html,
            'site_data': {
                'id': site.id,
                'pti_cell_id': site.pti_cell_id or '',
                'operator_id': site.operator_id or '',
                'name': site.name,
                'lat_base': site.lat_base,
                'lon_base': site.lon_base,
                'alt': site.alt or '',
                'region': site.region or '',
                'comuna': site.comuna or '',
            }
        })

    def post(self, request, site_id):
        try:
            site = get_object_or_404(Site, id=site_id)
            
            # Parsear el JSON del body
            data = json.loads(request.body.decode('utf-8'))
            
            # Convertir valores vacíos a None para campos numéricos
            if data.get('lat_base') == '':
                data['lat_base'] = None
            if data.get('lon_base') == '':
                data['lon_base'] = None
            
            # Manejar el campo user correctamente
            if 'user' in data:
                if data['user'] == '' or data['user'] is None:
                    # Si el campo está vacío, establecer como None
                    data['user'] = None
                else:
                    try:
                        # Convertir a entero si es string
                        user_id = int(data['user'])
                        # Verificar que el usuario existe
                        from users.models import User
                        user = User.objects.get(id=user_id)
                        data['user'] = user_id
                        
                    except (ValueError, TypeError, User.DoesNotExist) as e:
                        
                        # Si no se puede convertir o el usuario no existe, eliminar el campo
                        del data['user']
                        
            form = SiteForm(data, instance=site)
            
            if form.is_valid():
                form.save()
                return JsonResponse({
                    'success': True,
                    'message': f'Sitio "{site.name}" actualizado correctamente.'
                })
            else:
                print(f"Form errors: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'message': 'Error en el formulario.',
                    'errors': form.errors
                }, status=400)
                
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'message': 'Error al parsear los datos JSON.',
                'error': str(e)
            }, status=400)
        except Exception as e:
            print(f"Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor.',
                'error': str(e)
            }, status=500)