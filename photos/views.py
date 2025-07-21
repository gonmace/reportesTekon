from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import get_object_or_404
from core.utils.breadcrumbs import BreadcrumbsMixin
from django.contrib.contenttypes.models import ContentType
import json
from .models import Photos


def get_registro_from_id(registro_id):
    """
    Función helper para obtener el registro basado en el ID.
    Intenta encontrar el registro en diferentes aplicaciones.
    """
    # Intentar con registros_txtss
    try:
        from registros_txtss.models import Registros
        return Registros.objects.get(id=registro_id)
    except:
        pass
    
    # Intentar con registros_test (comentado temporalmente)
    # try:
    #     from registros_test.models import Registros
    #     return Registros.objects.get(id=registro_id)
    # except:
    #     pass
    
    return None


class ListPhotosView(BreadcrumbsMixin, ListView):
    model = Photos
    template_name = 'pages/photos_list.html'
    context_object_name = 'photos'

    class Meta:
        title = 'Gestión de Imágenes'
        header_title = 'Gestión de Imágenes'

    def get_queryset(self):
        registro_id = self.kwargs['registro_id']
        title = self.kwargs['title']
        
        # Obtener el ContentType del modelo Registros
        from django.contrib.contenttypes.models import ContentType
        from registros_txtss.models import Registros
        
        content_type = ContentType.objects.get_for_model(Registros)
        
        return Photos.objects.filter(content_type=content_type, object_id=registro_id, etapa=title)

    def get_breadcrumbs(self):
        """Genera breadcrumbs dinámicos basados en el registro y etapa"""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
        ]
        
        # Obtener el nombre del sitio del registro
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            registro = get_registro_from_id(registro_id)
            if registro:
                try:
                    sitio_cod = registro.sitio.pti_cell_id
                except:
                    sitio_cod = registro.sitio.operator_id
                
                # Determinar la aplicación basada en el tipo de registro
                if hasattr(registro, '_meta') and registro._meta.app_label == 'registros_txtss':
                    breadcrumbs.append({'label': 'TX/TSS', 'url_name': 'registros_txtss:list'})
                    breadcrumbs.append({
                        'label': sitio_cod, 
                        'url_name': 'registros_txtss:steps',
                        'url_kwargs': {'registro_id': registro_id}
                    })
                # elif hasattr(registro, '_meta') and registro._meta.app_label == 'registros_test':
                #     breadcrumbs.append({'label': 'Registros Test', 'url_name': 'registros_test:list'})
                #     breadcrumbs.append({
                #         'label': sitio_cod, 
                #         'url_name': 'registros_test:steps',
                #         'url_kwargs': {'registro_id': registro_id}
                #     })
                
                # Agregar el nivel de Photos
                breadcrumbs.append({'label': 'Photos'})
            else:
                breadcrumbs.append({'label': 'Registro'})
        else:
            breadcrumbs.append({'label': 'Registro'})
        
        return self._resolve_breadcrumbs(breadcrumbs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registro_id'] = self.kwargs['registro_id']
        context['title'] = self.kwargs['title']
        
        # Obtener información del registro para el contexto
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            registro = get_registro_from_id(registro_id)
            if registro:
                context['registro_txtss'] = registro
                context['sitio'] = registro.sitio
            else:
                context['error'] = 'Registro no encontrado'
        
        return context

@method_decorator(csrf_exempt, name='dispatch')
class UploadPhotosView(View):
    def post(self, request, registro_id, title):
        try:
            # Verificar que el registro existe
            registro = get_registro_from_id(registro_id)
            if not registro:
                return JsonResponse({
                    'success': False,
                    'message': f'Registro con ID {registro_id} no encontrado'
                }, status=400)
            
            files = request.FILES.getlist('photos')
            if not files:
                return JsonResponse({
                    'success': False,
                    'message': 'No se recibieron archivos'
                }, status=400)
            
            descripcion = request.POST.get('descripcion', '')
            
            photos_creadas = []
            for file in files:
                if file.content_type.startswith('image/'):
                    photo = Photos.objects.create(
                        imagen=file,
                        descripcion=descripcion,
                        registro=registro,
                        etapa=title
                    )
                    photos_creadas.append({
                        'id': photo.id,
                        'url': photo.imagen.url,
                        'descripcion': photo.descripcion,
                        'created_at': photo.created_at.strftime('%d/%m/%Y %H:%M')
                    })
            
            if not photos_creadas:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudieron procesar los archivos. Asegúrate de que sean imágenes válidas.'
                }, status=400)
            
            return JsonResponse({
                'success': True,
                'photos': photos_creadas,
                'message': f'Se subieron {len(photos_creadas)} fotos correctamente'
            })
        except Exception as e:
            import traceback
            print(f"Error en UploadPhotosView: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({
                'success': False,
                'message': f'Error al subir fotos: {str(e)}'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UpdatePhotoView(View):
    def post(self, request, registro_id, title):
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            descripcion = data.get('descripcion', '')
            photo = Photos.objects.get(id=photo_id)
            photo.descripcion = descripcion
            photo.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Descripción actualizada correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al actualizar: {str(e)}'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ReorderPhotosView(View):
    def post(self, request, registro_id, title):
        try:
            data = json.loads(request.body)
            orden = data.get('orden', [])
            
            for index, photo_id in enumerate(orden):
                Photos.objects.filter(id=photo_id).update(orden=index)
            
            return JsonResponse({
                'success': True,
                'message': 'Orden actualizado correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al reordenar: {str(e)}'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class DeletePhotoView(View):
    def post(self, request, registro_id, title, photo_id):
        try:
            photo = Photos.objects.get(id=photo_id)
            photo.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Foto eliminada correctamente'
            })
        except Photos.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Foto no encontrada'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar: {str(e)}'
            }, status=400)


