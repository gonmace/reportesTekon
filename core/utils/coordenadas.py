from geopy.distance import geodesic
import requests
import math
from core.models.app_settings import AppSettings

def calcular_distancia_geopy(lat_1, lon_1, lat_2, lon_2):
    """Calcula la distancia entre dos puntos usando geopy."""
    if lat_1 is not None and lon_1 is not None and lat_2 is not None and lon_2 is not None:
        try:
            # Asegurarse de que los valores sean float
            lat_1 = float(lat_1)
            lon_1 = float(lon_1)
            lat_2 = float(lat_2)
            lon_2 = float(lon_2)
            
            # Validar que los valores estén en rangos válidos
            if not (-90 <= lat_1 <= 90) or not (-90 <= lat_2 <= 90):
                return None
            if not (-180 <= lon_1 <= 180) or not (-180 <= lon_2 <= 180):
                return None
                
            origen_coords = (lat_1, lon_1)
            destino_coords = (lat_2, lon_2)
            # Calcula la distancia usando geodesic de geopy
            distancia = geodesic(origen_coords, destino_coords).meters
            return distancia
        except (ValueError, TypeError):
            return None
    else:
        return None


def calcular_distancia_entre_puntos(lat_1, lon_1, lat_2, lon_2):
    """Alias para calcular_distancia_geopy para compatibilidad."""
    return calcular_distancia_geopy(lat_1, lon_1, lat_2, lon_2)

def obtener_imagen_google_maps(coordenadas, zoom=None, maptype="hybrid", scale=2, tamano="1200x600"):
    """
    Función genérica para obtener imagen de Google Maps con cualquier número de coordenadas.
    
    Args:
        coordenadas: Lista de diccionarios con formato:
                    [{"lat": lat, "lon": lon, "color": color, "label": label, "size": size}, ...]
        zoom: Nivel de zoom (None para automático)
        maptype: Tipo de mapa ("hybrid", "roadmap", "satellite", "terrain")
        scale: Escala de la imagen (1 o 2)
        tamano: Tamaño de la imagen ("1200x600" por defecto, formato rectangular panorámico)
    
    Returns:
        bytes: Contenido de la imagen o None si hay error
    """
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    
    # Obtener la API key desde la configuración de la aplicación
    try:
        app_settings = AppSettings.get_actives()
        api_key = app_settings.google_maps_api_key if app_settings else None
        api_key = "AIzaSyCha-3YT1hTLafIM1rl7dv0-3lqEc5Drys"
        
        if not api_key:
            print("Error: No se encontró la Google Maps API key en la configuración de la aplicación")
            return None
            
    except Exception as e:
        print(f"Error obteniendo la API key: {e}")
        return None

    # Recolectar todos los puntos válidos
    puntos = []
    markers = []
    
    # Procesar cada coordenada
    for coord in coordenadas:
        lat = coord.get('lat')
        lon = coord.get('lon')
        color = coord.get('color', '0xFFFF00')
        label = coord.get('label', '')
        size = coord.get('size', 'mid')
        
        # Validar coordenadas
        if lat is not None and lon is not None:
            try:
                lat_float = float(lat)
                lon_float = float(lon)
                if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                    puntos.append((lat_float, lon_float))
                    
                    # Construir marcador
                    # Convertir color de formato # a formato 0x si es necesario
                    if color.startswith('#'):
                        color = '0x' + color[1:]  # Convertir #3B82F6 a 0x3B82F6
                    
                    # Usar el color sin transparencia para mejor visibilidad
                    marker_color = color
                    
                    marker = f"size:{size}|color:{marker_color}"
                    if label:
                        marker += f"|label:{label}"
                    marker += f"|{lat},{lon}"
                    markers.append(marker)
            except (ValueError, TypeError):
                continue
    
    # Si no hay puntos válidos, retornar None
    if not puntos:
        return None
    
    # Calcular centro y zoom automáticamente
    if len(puntos) == 1:
        centro_lat, centro_lon = puntos[0]
        zoom_auto = 20  # Zoom máximo de Google Maps
    else:
        # Calcular bounds
        lats = [p[0] for p in puntos]
        lons = [p[1] for p in puntos]
        centro_lat = (min(lats) + max(lats)) / 2
        centro_lon = (min(lons) + max(lons)) / 2
        
        # Calcular zoom basándose en el span
        max_span = max(max(lats) - min(lats), max(lons) - min(lons))
        
        # Calcular zoom máximo posible pero asegurando visibilidad de todos los puntos
        if max_span < 0.00001:  # Extremadamente cerca (menos de ~1 metro)
            zoom_auto = 20  # Zoom máximo
        elif max_span < 0.0001:  # Muy cerca (menos de ~10 metros)
            zoom_auto = 20  # Zoom máximo
        elif max_span < 0.0005:  # Cerca (menos de ~50 metros)
            zoom_auto = 19  # Zoom muy alto
        elif max_span < 0.001:   # Cerca (menos de ~100 metros)
            zoom_auto = 18  # Zoom alto
        elif max_span < 0.005:   # Moderado (menos de ~500 metros)
            zoom_auto = 17  # Zoom alto-medio
        elif max_span < 0.01:    # Moderado (menos de ~1 km)
            zoom_auto = 16  # Zoom medio-alto
        elif max_span < 0.05:    # Lejos (menos de ~5 km)
            zoom_auto = 15  # Zoom medio
        elif max_span < 0.1:     # Lejos (menos de ~10 km)
            zoom_auto = 14  # Zoom medio-bajo
        else:                    # Muy lejos (más de 10 km)
            zoom_auto = 13  # Zoom bajo pero visible
    
    # Usar zoom automático si no se especifica uno
    if zoom is None:
        zoom = zoom_auto
    
    centro = f"{centro_lat},{centro_lon}"
    
    params = {
        "center": centro,
        "zoom": zoom,
        "size": tamano,
        "maptype": maptype,
        "scale": scale,
        "key": api_key,
        "markers": markers,
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Error en la respuesta de Google Maps API: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con Google Maps API: {e}")
        return None