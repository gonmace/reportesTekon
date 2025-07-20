"""
Ejemplo de uso de la nueva arquitectura de elementos con sub-elementos.

Este archivo muestra cómo crear elementos específicos que están asociados
a un formulario y un modelo específico, y cómo agregar sub-elementos como
fotos, mapas, tablas, etc.
"""

from .base import ElementoRegistro
from .factory import ElementoFactory, SubElementoFactory


# Ejemplo de clases de elementos específicos
# Estas clases están definidas en registros_txtss/elementos.py

# from registros_txtss.elementos import ElementoSitio, ElementoAcceso, ElementoEmpalme


def ejemplo_uso_elementos_con_sub_elementos():
    """
    Ejemplo de cómo usar elementos específicos con sub-elementos.
    """
    # Este ejemplo requiere que las clases ElementoSitio, ElementoAcceso, etc.
    # estén definidas en las aplicaciones específicas
    
    # from registros_txtss.models import Registros
    # from registros_txtss.elementos import ElementoSitio, ElementoAcceso, ElementoEmpalme
    
    # # Obtener un registro
    # registro = Registros.objects.first()
    
    # # Crear elementos específicos con sub-elementos
    # elemento_sitio = ElementoSitio(registro)
    # elemento_acceso = ElementoAcceso(registro)
    # elemento_empalme = ElementoEmpalme(registro)
    
    # # Obtener instancias existentes
    # instancia_sitio = elemento_sitio.get_or_create()
    # instancia_acceso = elemento_acceso.get_or_create()
    # instancia_empalme = elemento_empalme.get_or_create()
    
    # # Si hay instancias, crear elementos con ellas
    # if instancia_sitio:
    #     elemento_sitio = ElementoSitio(registro, instancia_sitio)
    # if instancia_acceso:
    #     elemento_acceso = ElementoAcceso(registro, instancia_acceso)
    # if instancia_empalme:
    #     elemento_empalme = ElementoEmpalme(registro, instancia_empalme)
    
    # # Obtener formularios
    # form_sitio = elemento_sitio.get_form()
    # form_acceso = elemento_acceso.get_form()
    # form_empalme = elemento_empalme.get_form()
    
    # # Obtener sub-elementos
    # sub_elementos_sitio = elemento_sitio.get_all_sub_elementos()
    # sub_elementos_acceso = elemento_acceso.get_all_sub_elementos()
    # sub_elementos_empalme = elemento_empalme.get_all_sub_elementos()
    
    # return {
    #     'sitio': {
    #         'elemento': elemento_sitio,
    #         'form': form_sitio,
    #         'instance': instancia_sitio,
    #         'sub_elementos': sub_elementos_sitio,
    #     },
    #     'acceso': {
    #         'elemento': elemento_acceso,
    #         'form': form_acceso,
    #         'instance': instancia_acceso,
    #         'sub_elementos': sub_elementos_acceso,
    #     },
    #     'empalme': {
    #         'elemento': elemento_empalme,
    #         'form': form_empalme,
    #         'instance': instancia_empalme,
    #         'sub_elementos': sub_elementos_empalme,
    #     },
    # }
    
    return {
        'message': 'Este ejemplo requiere clases específicas definidas en las aplicaciones'
    }


def ejemplo_uso_elementos_genericos_con_sub_elementos():
    """
    Ejemplo de cómo usar elementos genéricos con sub-elementos usando la factory.
    """
    # Este ejemplo muestra cómo usar la factory para crear elementos dinámicamente
    
    # from registros_txtss.models import Registros
    # from registros_txtss.r_sitio.models import RSitio
    # from registros_txtss.r_sitio.form import RSitioForm
    # from registros_txtss.r_acceso.models import RAcceso
    # from registros_txtss.r_acceso.form import RAccesoForm
    # from registros_txtss.r_empalme.models import REmpalme
    # from registros_txtss.r_empalme.form import REmpalmeForm
    
    # # Obtener un registro
    # registro = Registros.objects.first()
    
    # # Crear elementos genéricos con sub-elementos específicos
    # elemento_form_sitio = ElementoFactory.create_elemento(
    #     registro=registro,
    #     model=RSitio,
    #     form_class=RSitioForm,
    #     sub_elementos=['map', 'photos', 'table']
    # )
    
    # elemento_form_acceso = ElementoFactory.create_elemento(
    #     registro=registro,
    #     model=RAcceso,
    #     form_class=RAccesoForm,
    #     sub_elementos=['map', 'photos']
    # )
    
    # elemento_form_empalme = ElementoFactory.create_elemento(
    #     registro=registro,
    #     model=REmpalme,
    #     form_class=REmpalmeForm,
    #     sub_elementos=['map', 'photos', 'chart']
    # )
    
    # # Obtener formularios
    # form_sitio = elemento_form_sitio.get_form()
    # form_acceso = elemento_form_acceso.get_form()
    # form_empalme = elemento_form_empalme.get_form()
    
    # # Obtener sub-elementos
    # sub_elementos_sitio = elemento_form_sitio.get_all_sub_elementos()
    # sub_elementos_acceso = elemento_form_acceso.get_all_sub_elementos()
    # sub_elementos_empalme = elemento_form_empalme.get_all_sub_elementos()
    
    # return {
    #     'sitio': {
    #         'elemento': elemento_form_sitio,
    #         'form': form_sitio,
    #         'sub_elementos': sub_elementos_sitio,
    #     },
    #     'acceso': {
    #         'elemento': elemento_form_acceso,
    #         'form': form_acceso,
    #         'sub_elementos': sub_elementos_acceso,
    #     },
    #     'empalme': {
    #         'elemento': elemento_form_empalme,
    #         'form': form_empalme,
    #         'sub_elementos': sub_elementos_empalme,
    #     },
    # }
    
    return {
        'message': 'Este ejemplo requiere modelos y formularios específicos'
    }


def ejemplo_uso_sub_elementos_individuales():
    """
    Ejemplo de cómo usar sub-elementos individuales.
    """
    # Este ejemplo muestra cómo acceder a sub-elementos individuales
    
    # from registros_txtss.models import Registros
    # from registros_txtss.elementos import ElementoSitio
    
    # # Obtener un registro
    # registro = Registros.objects.first()
    
    # # Crear un elemento base
    # elemento_sitio = ElementoSitio(registro)
    
    # # Obtener sub-elementos individuales
    # sub_elemento_map = elemento_sitio.get_sub_elemento('map')
    # sub_elemento_photos = elemento_sitio.get_sub_elemento('photos')
    # sub_elemento_table = elemento_sitio.get_sub_elemento('table')
    
    # # Obtener datos de cada sub-elemento
    # datos_mapa = sub_elemento_map.get_data()
    # datos_fotos = sub_elemento_photos.get_data()
    # datos_tabla = sub_elemento_table.get_data()
    
    # return {
    #     'elemento': elemento_sitio,
    #     'sub_elementos': {
    #         'map': {
    #             'instancia': sub_elemento_map,
    #             'datos': datos_mapa,
    #         },
    #         'photos': {
    #             'instancia': sub_elemento_photos,
    #             'datos': datos_fotos,
    #         },
    #         'table': {
    #             'instancia': sub_elemento_table,
    #             'datos': datos_tabla,
    #         },
    #     },
    # }
    
    return {
        'message': 'Este ejemplo requiere una clase ElementoSitio definida'
    }


def ejemplo_uso_en_vista():
    """
    Ejemplo de cómo usar elementos con sub-elementos en una vista.
    """
    from django.http import JsonResponse
    from .utils import handle_elemento_ajax_request
    
    def vista_elemento_sitio(request, registro_id):
        try:
            # from registros_txtss.models import Registros
            # from registros_txtss.elementos import ElementoSitio
            
            # registro = Registros.objects.get(id=registro_id)
            
            # # Crear elemento de sitio con sub-elementos
            # elemento = ElementoSitio(registro)
            
            # # Obtener instancia existente
            # instancia = elemento.get_or_create()
            # if instancia:
            #     elemento = ElementoSitio(registro, instancia)
            
            # # Manejar la petición
            # return handle_elemento_ajax_request(request, elemento)
            
            return JsonResponse({'message': 'Esta vista requiere clases específicas definidas'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return vista_elemento_sitio


def ejemplo_uso_implementado():
    """
    Ejemplo de uso con las clases ya implementadas.
    """
    try:
        from registros_txtss.models import Registros
        from registros_txtss.elementos import ElementoSitio
        
        # Obtener un registro
        registro = Registros.objects.first()
        if not registro:
            return {'message': 'No hay registros disponibles'}
        
        # Crear elemento de sitio
        elemento_sitio = ElementoSitio(registro)
        
        # Obtener instancia existente
        instancia = elemento_sitio.get_or_create()
        if instancia:
            elemento_sitio = ElementoSitio(registro, instancia)
        
        # Obtener formulario
        form = elemento_sitio.get_form()
        
        # Obtener sub-elementos
        sub_elementos = elemento_sitio.get_all_sub_elementos()
        
        # Obtener información de completitud
        completeness_info = elemento_sitio.get_completeness_info()
        
        return {
            'success': True,
            'elemento': {
                'tipo': elemento_sitio.tipo,
                'model': elemento_sitio.model.__name__,
                'has_instance': instancia is not None,
                'completeness_info': completeness_info,
            },
            'form': {
                'fields': list(form.fields.keys()) if form else [],
                'is_valid': form.is_valid() if form else False,
            },
            'sub_elementos': {
                tipo: {
                    'tipo': sub_elemento.tipo,
                    'has_data': bool(sub_elemento.get_data()),
                }
                for tipo, sub_elemento in sub_elementos.items()
            },
            'urls': {
                'form': f'/txtss/registros/{registro.id}/elemento/sitio/form/',
                'api': f'/txtss/registros/{registro.id}/elemento/sitio/',
            }
        }
        
    except ImportError as e:
        return {
            'success': False,
            'error': f'Error de importación: {str(e)}',
            'message': 'Asegúrate de que las clases estén correctamente definidas'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': 'Error al ejecutar el ejemplo'
        } 