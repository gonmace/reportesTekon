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
from django.apps import apps
from django.http import Http404

def get_registro_from_id(registro_id):
    """
    Función helper para obtener el registro basado en el ID.
    Intenta encontrar el registro en diferentes aplicaciones.
    """
    # Intentar con reg_txtss
    try:
        from reg_txtss.models import RegTxtss
        return RegTxtss.objects.get(id=registro_id)
    except:
        pass
    
    # Intentar con registros_test (comentado temporalmente)
    # try:
    #     from registros_test.models import Registros
    #     return Registros.objects.get(id=registro_id)
    # except:
    #     pass
    
    return None


def get_app_name_from_registro(registro):
    """
    Función helper para determinar el app_name basado en el tipo de registro.
    """
    if not registro:
        return None
    
    app_label = registro._meta.app_label
    
    # Mapeo de app_label a app_name
    app_mapping = {
        'reg_txtss': 'txtss',
        'registros_txtss': 'txtss',  # Mantener compatibilidad
        'registros_test': 'test',
        # Agregar más mapeos según sea necesario
    }
    
    return app_mapping.get(app_label)


def get_app_name_from_registro_id(registro_id):
    """
    Función helper para obtener el app_name basado en el ID del registro.
    """
    registro = get_registro_from_id(registro_id)
    return get_app_name_from_registro(registro)


class ListPhotosView(ListView):
    model = Photos
    template_name = 'pages/photos_list.html'
    context_object_name = 'photos'

    def get_queryset(self):
        app_name = self.kwargs.get('app_name')
        step_name = self.kwargs.get('step_name')
        paso_nombre = self.kwargs.get('paso_nombre')
        registro_id = self.kwargs.get('registro_id')
        
        # Si no hay registro_id en kwargs, intentar obtenerlo de la URL resuelta
        if not registro_id:
            # Intentar obtener de la URL resuelta
            resolved_url = self.request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        print("==================")
        print(self.kwargs)
        print("resolver_match:", self.request.resolver_match.kwargs if self.request.resolver_match else "None")
        print(app_name, step_name, paso_nombre, registro_id)
        print("==================")

        # Si no hay app_name, determinarlo dinámicamente basado en el registro
        if not app_name:
            app_name = get_app_name_from_registro_id(registro_id)
            if not app_name:
                # Fallback por defecto
                app_name = 'txtss'
        
        # Si no hay step_name, intentar obtenerlo de paso_nombre
        if not step_name:
            step_name = paso_nombre

        # Determinar el nombre de la app para el filtro
        app_filter = app_name
        if app_name == 'txtss':
            app_filter = 'reg_txtss'

        print(f"DEBUG: app_name={app_name}, app_filter={app_filter}, step_name={step_name}, registro_id={registro_id}")
        
        if step_name == 'sitio':
            from reg_txtss.models import RegTxtss
            model_class = RegTxtss
            etapa = 'sitio'
            object_id = registro_id
            print(f"DEBUG: Caso sitio - model_class={model_class}, etapa={etapa}, object_id={object_id}")
        else:
            try:
                model_class = apps.get_model(f"reg_{app_name}", f"R{step_name.capitalize()}")
                print(f"DEBUG: Modelo encontrado: {model_class}")
            except LookupError:
                print(f"DEBUG: Error - Modelo no encontrado para reg_{app_name}.R{step_name.capitalize()}")
                raise Http404("Modelo no encontrado")
            etapa = model_class.get_etapa()
            print(f"DEBUG: Etapa obtenida: {etapa}")
            # Buscar el objeto de la etapa correspondiente al registro principal
            try:
                etapa_obj = model_class.objects.get(registro_id=registro_id)
                object_id = etapa_obj.id
                print(f"DEBUG: Objeto de etapa encontrado: {etapa_obj}, object_id={object_id}")
            except model_class.DoesNotExist:
                object_id = None
                print(f"DEBUG: Objeto de etapa NO encontrado para registro_id={registro_id}")
        
        content_type = ContentType.objects.get_for_model(model_class)
        print(f"DEBUG: ContentType: {content_type}")
        print(f"DEBUG: object_id={object_id}, etapa={etapa}")
        
        # Si no hay object_id (no existe el objeto de la etapa), buscar fotos asociadas al registro principal
        if object_id is None:
            print("DEBUG: Objeto de etapa no existe, buscando fotos asociadas al registro principal")
            # Usar el registro principal como modelo
            from reg_txtss.models import RegTxtss
            content_type = ContentType.objects.get_for_model(RegTxtss)
            object_id = registro_id
        
        # Usar el campo app para filtrar las fotos
        queryset = Photos.objects.filter(
            app=app_filter,
            object_id=object_id,
            etapa=etapa
        )
        print(f"DEBUG: Queryset final: {queryset.count()} fotos encontradas")
        return queryset

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
                app_name = get_app_name_from_registro(registro)
                
                if app_name == 'txtss':
                    breadcrumbs.append({'label': 'TX/TSS', 'url_name': 'reg_txtss:list'})
                    breadcrumbs.append({
                        'label': sitio_cod, 
                        'url_name': 'reg_txtss:steps',
                        'url_kwargs': {'registro_id': registro_id}
                    })
                elif app_name == 'test':
                    breadcrumbs.append({'label': 'Registros Test', 'url_name': 'registros_test:list'})
                    breadcrumbs.append({
                        'label': sitio_cod, 
                        'url_name': 'registros_test:steps',
                        'url_kwargs': {'registro_id': registro_id}
                    })
                # Agregar más casos según sea necesario
                
                # Agregar el nivel de Photos
                breadcrumbs.append({'label': 'Photos'})
            else:
                breadcrumbs.append({'label': 'Registro'})
        else:
            breadcrumbs.append({'label': 'Registro'})
        
        return self._resolve_breadcrumbs(breadcrumbs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener app_name y step_name de manera consistente
        app_name = self.kwargs.get('app_name')
        step_name = self.kwargs.get('step_name')
        paso_nombre = self.kwargs.get('paso_nombre')
        registro_id = self.kwargs.get('registro_id')
        
        # Si no hay registro_id en kwargs, intentar obtenerlo de la URL resuelta
        if not registro_id:
            # Intentar obtener de la URL resuelta
            resolved_url = self.request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        context['registro_id'] = registro_id
        
        # Si no hay app_name, determinarlo dinámicamente basado en el registro
        if not app_name:
            app_name = get_app_name_from_registro_id(registro_id)
            if not app_name:
                # Fallback por defecto
                app_name = 'txtss'
        
        # Si no hay step_name, intentar obtenerlo de paso_nombre
        if not step_name:
            step_name = paso_nombre
            
        context['app_name'] = app_name
        context['step_name'] = step_name
        
        # Obtener el título de la etapa o paso
        title = self.kwargs.get('title')
        if not title:
            title = step_name or 'sitio'
        context['title'] = title
        
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
    def post(self, request, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        # Si no hay registro_id en kwargs, intentar obtenerlo de la URL resuelta
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        # Si no hay step_name, usar paso_nombre
        if not step_name:
            step_name = paso_nombre
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
            
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(type(registro))
            
            # Determinar el nombre de la app
            app_name = get_app_name_from_registro(registro)
            app_filter = app_name
            if app_name == 'txtss':
                app_filter = 'reg_txtss'
            
            photos_creadas = []
            for file in files:
                if file.content_type.startswith('image/'):
                    photo = Photos.objects.create(
                        imagen=file,
                        descripcion=descripcion,
                        app=app_filter,
                        content_type=content_type,
                        object_id=registro.id,
                        etapa=step_name
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
    def post(self, request, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        # Si no hay registro_id en kwargs, intentar obtenerlo de la URL resuelta
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        # Si no hay step_name, usar paso_nombre
        if not step_name:
            step_name = paso_nombre
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            descripcion = data.get('descripcion', '')
            # Obtener el modelo de la etapa
            if step_name == 'sitio':
                from reg_txtss.models import RegTxtss
                model_class = RegTxtss
                etapa = 'sitio'
                object_id = registro_id
            else:
                from django.apps import apps
                try:
                    model_class = apps.get_model(f"reg_{app_name}", f"R{step_name.capitalize()}")
                except LookupError:
                    return JsonResponse({'success': False, 'message': 'Modelo no encontrado'}, status=404)
                etapa = model_class.get_etapa()
                try:
                    etapa_obj = model_class.objects.get(registro_id=registro_id)
                    object_id = etapa_obj.id
                except model_class.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Etapa no encontrada'}, status=404)
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(model_class)
            
            # Determinar el nombre de la app para el filtro
            app_filter = app_name
            if app_name == 'txtss':
                app_filter = 'reg_txtss'
            
            # Buscar la foto de forma robusta
            try:
                photo = Photos.objects.get(id=photo_id, app=app_filter, object_id=object_id, etapa=etapa)
            except Photos.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
            photo.descripcion = descripcion
            photo.save()
            return JsonResponse({'success': True, 'message': 'Descripción actualizada correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar: {str(e)}'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ReorderPhotosView(View):
    def post(self, request, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        # Si no hay registro_id en kwargs, intentar obtenerlo de la URL resuelta
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        # Si no hay step_name, usar paso_nombre
        if not step_name:
            step_name = paso_nombre
        try:
            data = json.loads(request.body)
            orden = data.get('orden', [])
            # Obtener el modelo de la etapa
            if step_name == 'sitio':
                from reg_txtss.models import RegTxtss
                model_class = RegTxtss
                etapa = 'sitio'
                object_id = registro_id
            else:
                from django.apps import apps
                try:
                    model_class = apps.get_model(f"reg_{app_name}", f"R{step_name.capitalize()}")
                except LookupError:
                    return JsonResponse({'success': False, 'message': 'Modelo no encontrado'}, status=404)
                etapa = model_class.get_etapa()
                try:
                    etapa_obj = model_class.objects.get(registro_id=registro_id)
                    object_id = etapa_obj.id
                except model_class.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Etapa no encontrada'}, status=404)
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(model_class)
            
            # Determinar el nombre de la app para el filtro
            app_filter = app_name
            if app_name == 'txtss':
                app_filter = 'reg_txtss'
            
            # Solo reordenar fotos de la etapa y objeto correctos
            for index, photo_id in enumerate(orden):
                Photos.objects.filter(id=photo_id, app=app_filter, object_id=object_id, etapa=etapa).update(orden=index)
            return JsonResponse({'success': True, 'message': 'Orden actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al reordenar: {str(e)}'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class DeletePhotoView(View):
    def post(self, request, photo_id, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        # Obtener parámetros de la URL resuelta si no están en kwargs
        resolved_url = request.resolver_match
        if resolved_url and hasattr(resolved_url, 'kwargs'):
            if not registro_id:
                registro_id = resolved_url.kwargs.get('registro_id')
            if not paso_nombre:
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        
        # Si no hay step_name, usar paso_nombre
        if not step_name:
            step_name = paso_nombre
            
        # Si no hay app_name, determinarlo dinámicamente
        if not app_name:
            app_name = get_app_name_from_registro_id(registro_id)
            if not app_name:
                app_name = 'txtss'
            
        print(f"DEBUG DeletePhotoView: photo_id={photo_id}, registro_id={registro_id}, paso_nombre={paso_nombre}, app_name={app_name}, step_name={step_name}")
        
        try:
            # Obtener el modelo de la etapa
            if step_name == 'sitio':
                from reg_txtss.models import RegTxtss
                model_class = RegTxtss
                etapa = 'sitio'
                object_id = registro_id
                print(f"DEBUG DeletePhotoView: Usando modelo RegTxtss para sitio, object_id: {object_id}")
            else:
                # Para etapas específicas, siempre usar el modelo principal (RegTxtss)
                from reg_txtss.models import RegTxtss
                model_class = RegTxtss
                etapa = step_name
                object_id = registro_id
                print(f"DEBUG DeletePhotoView: Usando modelo RegTxtss para etapa {step_name}, object_id: {object_id}")
            from django.contrib.contenttypes.models import ContentType
            content_type = ContentType.objects.get_for_model(model_class)
            
            # Determinar el nombre de la app para el filtro
            app_filter = app_name
            if app_name == 'txtss':
                app_filter = 'reg_txtss'
            
            # Buscar la foto de forma robusta
            try:
                photo = Photos.objects.get(id=photo_id, app=app_filter, object_id=object_id, etapa=etapa)
            except Photos.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
            photo.delete()
            return JsonResponse({'success': True, 'message': 'Foto eliminada correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar: {str(e)}'}, status=400)


