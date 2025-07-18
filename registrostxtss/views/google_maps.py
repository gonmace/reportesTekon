from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from core.utils.coordenadas import obtener_imagen_google_maps, calcular_distancia_geopy
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from registrostxtss.models import MapaDesfase, RegistrosTxTss
import json
import os
from datetime import datetime
from django.conf import settings


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
            "coordenada_2": {
                "lat": -33.4568,
                "lon": -70.6484,
                "label": "I", 
                "color": "#EF4444",
                "size": "mid"
            },
            "zoom": 15,
            "maptype": "hybrid",
            "scale": 2,
            "tamano": "1200x600"
        }
        """
        try:
            # Obtener datos
            registro_id = request.data.get('registro_id')
            coord_1 = request.data.get('coordenada_1', {})
            coord_2 = request.data.get('coordenada_2', {})
            zoom = request.data.get('zoom')
            maptype = request.data.get('maptype', 'hybrid')
            scale = request.data.get('scale', 2)
            tamano = request.data.get('tamano', '1200x600')
            
            # Validar registro_id
            if not registro_id:
                return Response({
                    'error': 'registro_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                registro = RegistrosTxTss.objects.get(id=registro_id)
            except RegistrosTxTss.DoesNotExist:
                return Response({
                    'error': f'Registro con ID {registro_id} no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validar coordenadas requeridas
            if not coord_1 or 'lat' not in coord_1 or 'lon' not in coord_1:
                return Response({
                    'error': 'coordenada_1 debe tener lat y lon'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not coord_2 or 'lat' not in coord_2 or 'lon' not in coord_2:
                return Response({
                    'error': 'coordenada_2 debe tener lat y lon'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Preparar coordenadas para la función
            coordenadas = [
                {
                    'lat': coord_1['lat'],
                    'lon': coord_1['lon'],
                    'color': coord_1.get('color', '#3B82F6'),
                    'label': coord_1.get('label', 'M'),
                    'size': coord_1.get('size', 'large')
                },
                {
                    'lat': coord_2['lat'],
                    'lon': coord_2['lon'],
                    'color': coord_2.get('color', '#EF4444'),
                    'label': coord_2.get('label', 'I'),
                    'size': coord_2.get('size', 'mid')
                }
            ]
            
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
                    'error': 'No se pudo obtener la imagen de Google Maps'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Calcular distancia entre los puntos
            distancia = calcular_distancia_geopy(
                coord_1['lat'], coord_1['lon'],
                coord_2['lat'], coord_2['lon']
            )
            
            # Generar nombre único para el archivo usando código PTI y operador
            pti_code = registro.sitio.pti_cell_id or 'SIN_PTI'
            operator_code = registro.sitio.operator_id or 'SIN_OPERADOR'
            filename = f"{pti_code}_{operator_code}.png"
            
            # Guardar la imagen en el sistema de archivos y en la base de datos
            try:
                # Crear el directorio si no existe
                upload_dir = 'rsitio'
                media_root = settings.MEDIA_ROOT
                full_upload_dir = os.path.join(media_root, upload_dir)
                
                if not os.path.exists(full_upload_dir):
                    os.makedirs(full_upload_dir, exist_ok=True)
                
                # Guardar el archivo
                file_path = os.path.join(upload_dir, filename)
                saved_path = default_storage.save(file_path, ContentFile(imagen_bytes))
                
                # Crear registro en la base de datos
                mapa_desfase = MapaDesfase.objects.create(
                    registro=registro,
                    archivo=saved_path,
                    desfase_metros=distancia
                )
                
                # URL relativa del archivo guardado
                file_url = default_storage.url(saved_path)
                
                return Response({
                    'success': True,
                    'message': 'Imagen guardada exitosamente',
                    'mapa_id': mapa_desfase.id,
                    'file_path': saved_path,
                    'file_url': file_url,
                    'desfase_metros': distancia,
                    'parameters': {
                        'coordenada_1': coord_1,
                        'coordenada_2': coord_2,
                        'zoom': zoom,
                        'maptype': maptype,
                        'scale': scale,
                        'tamano': tamano
                    }
                })
                
            except Exception as save_error:
                return Response({
                    'error': f'Error al guardar la imagen: {str(save_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            return Response({
                'error': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 