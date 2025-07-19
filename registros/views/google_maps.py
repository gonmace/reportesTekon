from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from core.utils.coordenadas import obtener_imagen_google_maps, calcular_distancia_geopy
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from registros.models import MapasGoogle, Registros
import json
import os
from datetime import datetime
from django.conf import settings
from django.utils import timezone


class GoogleMapsView(APIView):
    """
    API View para obtener imágenes de Google Maps.
    Maneja tanto imágenes simples como imágenes de desfase entre puntos.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Obtener imagen de Google Maps y guardarla en el servidor.
        
        Body JSON esperado:
        {
            "registro_id": 123,
            "coordenada_1": {
                "lat": -33.4567,
                "lon": -70.6483,
                "label": "M",
                "color": "#3B82F6",
                "size": "large"
            },
            "coordenada_2": {  # Opcional
                "lat": -33.4568,
                "lon": -70.6484,
                "label": "I", 
                "color": "#EF4444",
                "size": "mid"
            },
            "coordenada_3": {  # Opcional
                "lat": -33.4569,
                "lon": -70.6485,
                "label": "P", 
                "color": "#8B5CF6",
                "size": "large"
            },
            // Se pueden agregar más coordenadas: coordenada_4, coordenada_5, etc.
            "zoom": 15,
            "maptype": "hybrid",
            "scale": 2,
            "tamano": "1200x600"
        }
        """
        try:
            # Obtener datos
            registro_id = request.data.get('registro_id')
            zoom = request.data.get('zoom')
            maptype = request.data.get('maptype', 'hybrid')
            scale = request.data.get('scale', 2)
            tamano = request.data.get('tamano', '1200x600')
            etapa = request.data.get('etapa', 'sitio')
            
            # Obtener todas las coordenadas disponibles
            coordinates = []
            for i in range(1, 10):  # Soporte para hasta 9 coordenadas
                coord_key = f'coordenada_{i}'
                coord_data = request.data.get(coord_key, {})
                if coord_data and 'lat' in coord_data and 'lon' in coord_data:
                    coordinates.append(coord_data)
            # Validar registro_id
            if not registro_id:
                return Response({
                    'error': 'registro_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                registro = Registros.objects.get(id=registro_id)
            except Registros.DoesNotExist:
                return Response({
                    'error': f'Registro con ID {registro_id} no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validar que al menos una coordenada sea válida
            if not coordinates:
                return Response({
                    'error': 'Se requiere al menos una coordenada válida'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preparar coordenadas para la función
            coordenadas = []
            for coord in coordinates:
                coordenadas.append({
                    'lat': coord['lat'],
                    'lon': coord['lon'],
                    'color': coord.get('color', '#3B82F6'),
                    'label': coord.get('label', 'P'),
                    'size': coord.get('size', 'large')
                })
            
            # Obtener la imagen
            imagen_bytes = obtener_imagen_google_maps(
                coordenadas=coordenadas,
                zoom=zoom,
                maptype=maptype,
                scale=scale,
                tamano=tamano
            )
            
            if imagen_bytes is None:
                return Response({
                    'error': 'No se pudo obtener la imagen de Google Maps. Verifique que la API key esté configurada correctamente en la configuración de la aplicación.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Calcular distancia total entre puntos consecutivos
            distancia_total = None
            if len(coordinates) > 1:
                distancia_total = 0
                for i in range(len(coordinates) - 1):
                    dist = calcular_distancia_geopy(
                        coordinates[i]['lat'], coordinates[i]['lon'],
                        coordinates[i + 1]['lat'], coordinates[i + 1]['lon']
                    )
                    if dist:
                        distancia_total += dist
            
            # Generar nombre único para el archivo usando código PTI, operador y etapa
            pti_code = registro.sitio.pti_cell_id or 'SIN_PTI'
            operator_code = registro.sitio.operator_id or 'SIN_OPERADOR'
            filename = f"{pti_code}_{operator_code}_{etapa}.png"
            
            # Guardar la imagen en el sistema de archivos y en la base de datos
            try:
                # Crear el directorio si no existe
                upload_dir = 'google_maps'
                media_root = settings.MEDIA_ROOT
                full_upload_dir = os.path.join(media_root, upload_dir)
                
                if not os.path.exists(full_upload_dir):
                    os.makedirs(full_upload_dir, exist_ok=True)
                
                # Guardar el archivo
                file_path = os.path.join(upload_dir, filename)
                saved_path = default_storage.save(file_path, ContentFile(imagen_bytes))
                
                # Buscar si existe un registro con el mismo registro y etapa
                existing_mapa = MapasGoogle.objects.filter(
                    registro=registro,
                    etapa=etapa
                ).first()
                
                # Si existe un registro anterior, eliminar su archivo físico
                if existing_mapa and existing_mapa.archivo:
                    try:
                        # Eliminar el archivo físico anterior si existe
                        if default_storage.exists(existing_mapa.archivo.name):
                            default_storage.delete(existing_mapa.archivo.name)
                    except Exception as e:
                        # Si hay error al eliminar el archivo, continuar
                        print(f"Error eliminando archivo anterior {existing_mapa.archivo.name}: {e}")
                
                # Crear o actualizar registro en la base de datos
                # Si existe un registro con el mismo registro y etapa, se reemplaza
                mapa_desfase, created = MapasGoogle.objects.update_or_create(
                    registro=registro,
                    etapa=etapa,
                    defaults={
                        'archivo': saved_path,
                        'fecha_creacion': timezone.now()
                    }
                )
                
                # URL relativa del archivo guardado
                file_url = default_storage.url(saved_path)
                
                action_message = 'Imagen actualizada exitosamente' if not created else 'Imagen guardada exitosamente'
                
                response_data = {
                    'success': True,
                    'message': action_message,
                    'mapa_id': mapa_desfase.id,
                    'file_path': saved_path,
                    'file_url': file_url,
                    'was_created': created,
                    'parameters': {
                        'zoom': zoom,
                        'maptype': maptype,
                        'scale': scale,
                        'tamano': tamano,
                        'coordenadas': coordinates
                    }
                }
                
                # Agregar distancia total solo si hay múltiples coordenadas
                if distancia_total is not None:
                    response_data['distancia_total_metros'] = distancia_total
                
                return Response(response_data)
                
            except Exception as save_error:
                return Response({
                    'error': f'Error al guardar la imagen: {str(save_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 