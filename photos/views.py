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

# Diccionario global para almacenar templates personalizados
PHOTOS_TEMPLATES = {}

def set_photos_template(app_name, step_name, template_name):
    """
    Configura el template personalizado para una combinación específica de app_name y step_name.
    
    Args:
        app_name: Nombre de la aplicación
        step_name: Nombre del paso/etapa
        template_name: Nombre del template a usar
    """
    template_key = f"{app_name}_{step_name}"
    PHOTOS_TEMPLATES[template_key] = template_name

def set_photos_template_for_step(step_name, template_name):
    """
    Configura el template personalizado para un step_name específico, 
    independientemente del app_name.
    
    Args:
        step_name: Nombre del paso/etapa
        template_name: Nombre del template a usar
    """
    # Usar un patrón que funcione para cualquier app_name
    PHOTOS_TEMPLATES[f"*_{step_name}"] = template_name

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
    
    # Intentar con reg_construccion
    try:
        from reg_construccion.models import RegConstruccion
        return RegConstruccion.objects.get(id=registro_id)
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
        'reg_construccion': 'construccion',
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


class ListPhotosView(BreadcrumbsMixin, ListView):
    model = Photos
    context_object_name = 'photos'
    template_name = 'photos/photos_main.html'
    
    def get_template_names(self):
        """Retorna el template a usar, priorizando el template personalizado"""
        # Obtener el template personalizado del diccionario global
        app_name = self.kwargs.get('app_name')
        step_name = self.kwargs.get('step_name')
        paso_nombre = self.kwargs.get('paso_nombre')
        
        if not step_name:
            step_name = paso_nombre
            
        # Buscar template personalizado por app_name y step_name
        if app_name and step_name:
            # Primero buscar coincidencia exacta
            template_key = f"{app_name}_{step_name}"
            if template_key in PHOTOS_TEMPLATES:
                return [PHOTOS_TEMPLATES[template_key]]
            
            # Luego buscar patrón con wildcard
            wildcard_key = f"*_{step_name}"
            if wildcard_key in PHOTOS_TEMPLATES:
                return [PHOTOS_TEMPLATES[wildcard_key]]
        
        # Si no hay template personalizado, usar el por defecto
        return [self.template_name]

    def get_queryset(self):
        app_name = self.kwargs.get('app_name')
        step_name = self.kwargs.get('step_name')
        paso_nombre = self.kwargs.get('paso_nombre')
        registro_id = self.kwargs.get('registro_id')

        if not registro_id:
            resolved_url = self.request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')

        # Determinar app_name dinámicamente si no está
        if not app_name:
            app_name = get_app_name_from_registro_id(registro_id)
            if not app_name:
                raise Http404("No se pudo determinar la aplicación")

        # Determinar step_name dinámicamente si no está
        if not step_name:
            step_name = paso_nombre
        if not step_name:
            raise Http404("No se pudo determinar la etapa")

        registro = get_registro_from_id(registro_id)
        if not registro:
            raise Http404("Registro no encontrado")

        if step_name == 'sitio':
            model_class = type(registro)
            object_id = registro.id
            etapa = 'sitio'
        else:
            try:
                # Usar el app_label real del registro, no el app_name mapeado
                app_label = registro._meta.app_label
                model_class = apps.get_model(app_label, f"R{step_name.capitalize()}")
                etapa = model_class.get_etapa()
                try:
                    etapa_obj = model_class.objects.get(registro_id=registro_id)
                    object_id = etapa_obj.id
                except model_class.DoesNotExist:
                    object_id = None
            except LookupError:
                # Si no se encuentra el modelo de la etapa, usar el registro principal
                # Esto es útil para pasos que solo tienen componentes (como fotos)
                model_class = type(registro)
                object_id = registro.id
                etapa = step_name

        content_type = ContentType.objects.get_for_model(model_class)

        if object_id is None:
            # Si no existe el objeto de la etapa, no deberíamos mostrar fotos
            # porque las fotos están asociadas al objeto de la etapa específica
            return Photos.objects.none()

        # Buscar fotos asociadas al modelo específico de la etapa
        queryset = Photos.objects.filter(
            app=registro._meta.app_label,
            object_id=object_id,
            etapa=etapa,
            content_type=content_type
        )
        
        # Si no hay fotos, buscar también en el registro principal (compatibilidad con fotos existentes)
        if queryset.count() == 0 and step_name != 'sitio':
            registro_content_type = ContentType.objects.get_for_model(type(registro))
            queryset = Photos.objects.filter(
                app=registro._meta.app_label,
                object_id=registro.id,
                etapa=etapa,
                content_type=registro_content_type
            )
        
        # Debug: imprimir información para diagnóstico
        print(f"DEBUG - ListPhotosView.get_queryset:")
        print(f"  app: {registro._meta.app_label}")
        print(f"  object_id: {object_id}")
        print(f"  etapa: {etapa}")
        print(f"  step_name: {step_name}")
        print(f"  registro_id: {registro_id}")
        print(f"  queryset count: {queryset.count()}")
        
        return queryset

    def get_breadcrumbs(self):
        """Genera breadcrumbs dinámicos basados en el registro y etapa"""
        breadcrumbs = [
            {'label': 'Inicio', 'url_name': 'dashboard:dashboard'},
        ]
        registro_id = self.kwargs.get('registro_id')
        if registro_id:
            registro = get_registro_from_id(registro_id)
            if registro:
                try:
                    sitio_cod = registro.sitio.pti_cell_id
                except Exception:
                    sitio_cod = getattr(registro.sitio, 'operator_id', 'Sitio')
                app_namespace = registro._meta.app_label  # namespace real
                app_label = get_app_name_from_registro(registro) or app_namespace
                breadcrumbs.append({'label': app_label.upper() if app_label else 'Registro', 'url_name': f'{app_namespace}:list'})
                breadcrumbs.append({
                    'label': sitio_cod,
                    'url_name': f'{app_namespace}:steps',
                    'url_kwargs': {'registro_id': registro_id}
                })
                breadcrumbs.append({'label': 'Imágenes'})
            else:
                breadcrumbs.append({'label': 'Registro'})
        else:
            breadcrumbs.append({'label': 'Registro'})
        return self._resolve_breadcrumbs(breadcrumbs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        app_name = self.kwargs.get('app_name')
        step_name = self.kwargs.get('step_name')
        paso_nombre = self.kwargs.get('paso_nombre')
        registro_id = self.kwargs.get('registro_id')
        if not registro_id:
            resolved_url = self.request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        context['registro_id'] = registro_id
        if not app_name:
            app_name = get_app_name_from_registro_id(registro_id)
            if not app_name:
                raise Http404("No se pudo determinar la aplicación")
        if not step_name:
            step_name = paso_nombre
        context['app_name'] = app_name
        context['step_name'] = step_name
        title = self.kwargs.get('title')
        if not title:
            title = step_name or 'sitio'
        context['title'] = title
        if registro_id:
            registro = get_registro_from_id(registro_id)
            if registro:
                context['registro_txtss'] = registro
                context['sitio'] = registro.sitio
            else:
                context['error'] = 'Registro no encontrado'
        return context

    def get_header_title(self):
        step_name = self.kwargs.get('step_name')
        if not step_name:
            paso_nombre = self.kwargs.get('paso_nombre')
            step_name = paso_nombre
        if step_name:
            return step_name.capitalize()
        return super().get_header_title()

@method_decorator(csrf_exempt, name='dispatch')
class UploadPhotosView(View):
    def post(self, request, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        if not step_name:
            step_name = paso_nombre
        try:
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
            
            # Determinar el content_type y object_id según la etapa
            if step_name == 'sitio':
                model_class = type(registro)
                content_type = ContentType.objects.get_for_model(model_class)
                object_id = registro.id
            else:
                try:
                    app_label = registro._meta.app_label
                    model_class = apps.get_model(app_label, f"R{step_name.capitalize()}")
                    content_type = ContentType.objects.get_for_model(model_class)
                    try:
                        etapa_obj = model_class.objects.get(registro_id=registro_id)
                        object_id = etapa_obj.id
                    except model_class.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'message': f'No existe el registro de la etapa {step_name}. Debes crear primero el registro.'
                        }, status=400)
                except LookupError:
                    return JsonResponse({
                        'success': False,
                        'message': f'Modelo de etapa {step_name} no encontrado'
                    }, status=400)
            
            if not app_name:
                app_name = get_app_name_from_registro(registro)
            photos_creadas = []
            for file in files:
                if file.content_type.startswith('image/'):
                    photo = Photos.objects.create(
                        imagen=file,
                        descripcion=descripcion,
                        app=registro._meta.app_label,  # Usar el app_label real del registro
                        content_type=content_type,
                        object_id=object_id,
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
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        if not step_name:
            step_name = paso_nombre
        try:
            data = json.loads(request.body)
            photo_id = data.get('photo_id')
            descripcion = data.get('descripcion', '')
            registro = get_registro_from_id(registro_id)
            if not registro:
                return JsonResponse({'success': False, 'message': 'Registro no encontrado'}, status=404)
            if not app_name:
                app_name = get_app_name_from_registro(registro)
            if step_name == 'sitio':
                model_class = type(registro)
                etapa = 'sitio'
                object_id = registro.id
            else:
                try:
                    model_class = apps.get_model(app_name, f"R{step_name.capitalize()}")
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
            try:
                photo = Photos.objects.get(id=photo_id, app=registro._meta.app_label, object_id=object_id, etapa=etapa)
            except Photos.DoesNotExist:
                # Si no se encuentra, buscar en el registro principal (compatibilidad con fotos existentes)
                if step_name != 'sitio':
                    registro_content_type = ContentType.objects.get_for_model(type(registro))
                    try:
                        photo = Photos.objects.get(id=photo_id, app=registro._meta.app_label, object_id=registro.id, etapa=etapa, content_type=registro_content_type)
                    except Photos.DoesNotExist:
                        return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
                else:
                    return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
            photo.descripcion = descripcion
            photo.save()
            return JsonResponse({'success': True, 'message': 'Descripción actualizada correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al actualizar: {str(e)}'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class ReorderPhotosView(View):
    def post(self, request, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        if not registro_id:
            resolved_url = request.resolver_match
            if resolved_url and hasattr(resolved_url, 'kwargs'):
                registro_id = resolved_url.kwargs.get('registro_id')
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        if not step_name:
            step_name = paso_nombre
        try:
            data = json.loads(request.body)
            orden = data.get('orden', [])
            registro = get_registro_from_id(registro_id)
            if not registro:
                return JsonResponse({'success': False, 'message': 'Registro no encontrado'}, status=404)
            if not app_name:
                app_name = get_app_name_from_registro(registro)
            if step_name == 'sitio':
                model_class = type(registro)
                etapa = 'sitio'
                object_id = registro.id
            else:
                try:
                    model_class = apps.get_model(app_name, f"R{step_name.capitalize()}")
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
            for index, photo_id in enumerate(orden):
                # Intentar actualizar en el modelo específico de la etapa
                updated = Photos.objects.filter(id=photo_id, app=registro._meta.app_label, object_id=object_id, etapa=etapa).update(orden=index)
                
                # Si no se actualizó, intentar en el registro principal (compatibilidad con fotos existentes)
                if updated == 0 and step_name != 'sitio':
                    registro_content_type = ContentType.objects.get_for_model(type(registro))
                    Photos.objects.filter(id=photo_id, app=registro._meta.app_label, object_id=registro.id, etapa=etapa, content_type=registro_content_type).update(orden=index)
            return JsonResponse({'success': True, 'message': 'Orden actualizado correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al reordenar: {str(e)}'}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class DeletePhotoView(View):
    def post(self, request, photo_id, registro_id=None, paso_nombre=None, app_name=None, step_name=None):
        resolved_url = request.resolver_match
        if resolved_url and hasattr(resolved_url, 'kwargs'):
            if not registro_id:
                registro_id = resolved_url.kwargs.get('registro_id')
            if not paso_nombre:
                paso_nombre = resolved_url.kwargs.get('paso_nombre')
        if not step_name:
            step_name = paso_nombre
        if not app_name:
            registro = get_registro_from_id(registro_id)
            if registro:
                app_name = get_app_name_from_registro(registro)
            if not app_name:
                app_name = None
        try:
            registro = get_registro_from_id(registro_id)
            if not registro:
                return JsonResponse({'success': False, 'message': 'Registro no encontrado'}, status=404)
            if step_name == 'sitio':
                model_class = type(registro)
                etapa = 'sitio'
                object_id = registro.id
            else:
                try:
                    model_class = apps.get_model(app_name, f"R{step_name.capitalize()}")
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
            try:
                photo = Photos.objects.get(id=photo_id, app=registro._meta.app_label, object_id=object_id, etapa=etapa)
            except Photos.DoesNotExist:
                # Si no se encuentra, buscar en el registro principal (compatibilidad con fotos existentes)
                if step_name != 'sitio':
                    registro_content_type = ContentType.objects.get_for_model(type(registro))
                    try:
                        photo = Photos.objects.get(id=photo_id, app=registro._meta.app_label, object_id=registro.id, etapa=etapa, content_type=registro_content_type)
                    except Photos.DoesNotExist:
                        return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
                else:
                    return JsonResponse({'success': False, 'message': 'Foto no encontrada'}, status=404)
            photo.delete()
            return JsonResponse({'success': True, 'message': 'Foto eliminada correctamente'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar: {str(e)}'}, status=400)


