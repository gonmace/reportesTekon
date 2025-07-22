#!/usr/bin/env python3
"""
Script de prueba para la API de Google Maps.
"""

import requests
import json

def test_google_maps_api():
    """Prueba la API de Google Maps."""
    
    # URL de la API
    url = 'http://localhost:8000/api/v1/google-maps/'
    
    # Datos de prueba
    test_data = {
        "registro_id": 1,  # Asumiendo que existe un registro con ID 1
        "etapa": "sitio",
        "coordenada_1": {
            "lat": -33.4567,
            "lon": -70.6483,
            "label": "I",
            "color": "#EF4444",
            "size": "large"
        },
        "coordenada_2": {
            "lat": -33.4568,
            "lon": -70.6484,
            "label": "M",
            "color": "#3B82F6",
            "size": "normal"
        },
        "zoom": 15,
        "maptype": "hybrid",
        "scale": 2,
        "tamano": "1200x600"
    }
    
    print("🧪 Probando API de Google Maps...")
    print(f"URL: {url}")
    print(f"Datos: {json.dumps(test_data, indent=2)}")
    
    try:
        # Hacer la petición POST
        response = requests.post(
            url,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': 'test-token'  # Token de prueba
            },
            timeout=30
        )
        
        print(f"\n📊 Respuesta:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Éxito: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que el servidor esté ejecutándose.")
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout en la petición.")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")

if __name__ == "__main__":
    test_google_maps_api() 