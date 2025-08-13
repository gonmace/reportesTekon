"""
Vistas para contratistas.
"""

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.forms import modelform_factory
from core.utils.breadcrumbs import BreadcrumbsMixin
from core.models.contractors import Contractor


class ContractorsView(LoginRequiredMixin, BreadcrumbsMixin, TemplateView):
    """Vista para listar contratistas."""
    template_name = 'pages/contractors.html'
    context_object_name = 'contractors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contractors'] = Contractor.objects.filter(is_active=True).order_by('name')
        return context

    @property
    def title(self):
        return 'Contratistas'

    @property
    def header_title(self):
        return 'Gestión de Contratistas'

    def get_breadcrumbs(self):
        return [
            {'label': 'Contratistas'}
        ]


class ContractorViewSet(View):
    """ViewSet para operaciones CRUD de contratistas."""
    
    def get(self, request):
        """Obtener lista de contratistas."""
        contractors = Contractor.objects.filter(is_active=True).order_by('name')
        data = []
        
        for contractor in contractors:
            data.append({
                'id': contractor.id,
                'name': contractor.name,
                'code': contractor.code,
                'is_active': contractor.is_active,
                'created_at': contractor.created_at.strftime('%d/%m/%Y %H:%M'),
                'updated_at': contractor.updated_at.strftime('%d/%m/%Y %H:%M'),
            })
        
        return JsonResponse(data, safe=False)

    def post(self, request):
        """Crear nuevo contratista."""
        try:
            data = request.POST.dict()
            
            # Crear el formulario dinámicamente
            ContractorForm = modelform_factory(Contractor, fields=['name', 'code'])
            form = ContractorForm(data)
            
            if form.is_valid():
                contractor = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Contratista creado correctamente',
                    'contractor': {
                        'id': contractor.id,
                        'name': contractor.name,
                        'code': contractor.code,
                        'is_active': contractor.is_active,
                        'created_at': contractor.created_at.strftime('%d/%m/%Y %H:%M'),
                        'updated_at': contractor.updated_at.strftime('%d/%m/%Y %H:%M'),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos del formulario',
                    'errors': form.errors
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al crear contratista: {str(e)}'
            }, status=500)

    def put(self, request, contractor_id):
        """Actualizar contratista existente."""
        try:
            contractor = Contractor.objects.get(id=contractor_id)
            data = request.POST.dict()
            
            # Crear el formulario dinámicamente
            ContractorForm = modelform_factory(Contractor, fields=['name', 'code'])
            form = ContractorForm(data, instance=contractor)
            
            if form.is_valid():
                contractor = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Contratista actualizado correctamente',
                    'contractor': {
                        'id': contractor.id,
                        'name': contractor.name,
                        'code': contractor.code,
                        'is_active': contractor.is_active,
                        'created_at': contractor.created_at.strftime('%d/%m/%Y %H:%M'),
                        'updated_at': contractor.updated_at.strftime('%d/%m/%Y %H:%M'),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Error en los datos del formulario',
                    'errors': form.errors
                }, status=400)
                
        except Contractor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Contratista no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar contratista: {str(e)}'
            }, status=500)

    def delete(self, request, contractor_id):
        """Eliminar contratista (marcar como inactivo)."""
        try:
            contractor = Contractor.objects.get(id=contractor_id)
            contractor.is_active = False
            contractor.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Contratista eliminado correctamente'
            })
                
        except Contractor.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Contratista no encontrado'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar contratista: {str(e)}'
            }, status=500)


class ContractorEditModalView(View):
    """Vista para mostrar/editar contratista en modal."""
    
    def get(self, request, contractor_id=None):
        """Mostrar formulario de contratista."""
        if contractor_id:
            try:
                contractor = Contractor.objects.get(id=contractor_id)
                action = 'edit'
            except Contractor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Contratista no encontrado'
                }, status=404)
        else:
            contractor = None
            action = 'create'
        
        # Crear el formulario dinámicamente
        ContractorForm = modelform_factory(Contractor, fields=['name', 'code'])
        form = ContractorForm(instance=contractor)
        
        # Aplicar clases de DaisyUI a los campos
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'input input-bordered w-full',
                'placeholder': f'Ingrese {field.label.lower()}'
            })
        
        form_html = render(request, 'components/contractor_form_modal.html', {
            'form': form,
            'contractor': contractor,
            'action': action
        }).content.decode('utf-8')
        
        return JsonResponse({
            'success': True,
            'form_html': form_html
        })

    def post(self, request, contractor_id=None):
        """Procesar formulario de contratista."""
        if contractor_id:
            try:
                contractor = Contractor.objects.get(id=contractor_id)
                action = 'edit'
            except Contractor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Contratista no encontrado'
                }, status=404)
        else:
            contractor = None
            action = 'create'
        
        # Crear el formulario dinámicamente
        ContractorForm = modelform_factory(Contractor, fields=['name', 'code'])
        form = ContractorForm(request.POST, instance=contractor)
        
        # Aplicar clases de DaisyUI a los campos
        for field_name, field in form.fields.items():
            field.widget.attrs.update({
                'class': 'input input-bordered w-full',
                'placeholder': f'Ingrese {field.label.lower()}'
            })
        
        if form.is_valid():
            contractor = form.save()
            return JsonResponse({
                'success': True,
                'message': f'Contratista {"actualizado" if action == "edit" else "creado"} correctamente',
                'contractor': {
                    'id': contractor.id,
                    'name': contractor.name,
                    'code': contractor.code,
                    'is_active': contractor.is_active,
                    'created_at': contractor.created_at.strftime('%d/%m/%Y %H:%M'),
                    'updated_at': contractor.updated_at.strftime('%d/%m/%Y %H:%M'),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Error en los datos del formulario',
                'errors': form.errors
            }, status=400)
