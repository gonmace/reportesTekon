from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Imagenes

class ListImagenesView(ListView):
    model = Imagenes
    template_name = 'pages/imagenes_list.html'
    context_object_name = 'imagenes'

@method_decorator(csrf_exempt, name='dispatch')
class UploadImagenesView(View):
    def post(self, request):
        try:
            files = request.FILES.getlist('imagenes')
            descripcion = request.POST.get('descripcion', '')
            registro_id = request.POST.get('registro_id')
            
            imagenes_creadas = []
            for file in files:
                if file.content_type.startswith('image/'):
                    imagen = Imagenes.objects.create(
                        imagen=file,
                        descripcion=descripcion,
                        registro_id=registro_id
                    )
                    imagenes_creadas.append({
                        'id': imagen.id,
                        'url': imagen.imagen.url,
                        'descripcion': imagen.descripcion,
                        'created_at': imagen.created_at.strftime('%d/%m/%Y %H:%M')
                    })
            
            return JsonResponse({
                'success': True,
                'imagenes': imagenes_creadas,
                'message': f'Se subieron {len(imagenes_creadas)} imágenes correctamente'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al subir imágenes: {str(e)}'
            }, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateImagenView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            imagen_id = data.get('imagen_id')
            descripcion = data.get('descripcion', '')
            
            imagen = Imagenes.objects.get(id=imagen_id)
            imagen.descripcion = descripcion
            imagen.save()
            
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
class ReorderImagenesView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            orden = data.get('orden', [])
            
            for index, imagen_id in enumerate(orden):
                Imagenes.objects.filter(id=imagen_id).update(orden=index)
            
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
class DeleteImagenView(View):
    def post(self, request, imagen_id):
        try:
            imagen = Imagenes.objects.get(id=imagen_id)
            imagen.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Imagen eliminada correctamente'
            })
        except Imagenes.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Imagen no encontrada'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error al eliminar: {str(e)}'
            }, status=400)


