from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Photos

class ListPhotosView(ListView):
    model = Photos
    template_name = 'pages/photos_list.html'
    context_object_name = 'photos'

    def get_queryset(self):
        registro_id = self.kwargs['registro_id']
        title = self.kwargs['title']
        return Photos.objects.filter(registro_id=registro_id, etapa=title)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registro_id'] = self.kwargs['registro_id']
        context['title'] = self.kwargs['title']
        return context

@method_decorator(csrf_exempt, name='dispatch')
class UploadPhotosView(View):
    def post(self, request, registro_id, title):
        try:
            # Verificar que el registro existe
            from registrostxtss.models.main_registrostxtss import RegistrosTxTss
            try:
                registro = RegistrosTxTss.objects.get(id=registro_id)
            except RegistrosTxTss.DoesNotExist:
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
                        registro_id=registro_id,
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


