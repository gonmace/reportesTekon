#!/usr/bin/env python3
"""
Debug script to check map coordinates data structure.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reg_txtss.models import RegTxtss, RSitio
from core.models.sites import Site
from registros.views.generic_registro_views import GenericRegistroStepsView
import json

def debug_map_coordinates():
    """Debug map coordinates data structure."""
    
    print("🔍 Debugging map coordinates...")
    
    # Get the first registro with sitio and rsitio
    try:
        registro = RegTxtss.objects.select_related('sitio').prefetch_related('rsitio_set').first()
        if not registro:
            print("❌ No registros found")
            return
        
        print(f"📋 Found registro: {registro.title}")
        print(f"   Sitio: {registro.sitio.name if registro.sitio else 'None'}")
        
        # Get RSitio instance
        rsitio = registro.rsitio_set.first()
        if not rsitio:
            print("❌ No RSitio instance found for this registro")
            return
        
        print(f"   RSitio: lat={rsitio.lat}, lon={rsitio.lon}")
        
        # Create a mock view instance
        class MockView(GenericRegistroStepsView):
            def get_registro_config(self):
                from reg_txtss.config import REGISTRO_CONFIG
                return REGISTRO_CONFIG
        
        view = MockView()
        
        # Get the sitio paso configuration
        sitio_paso = view.registro_config.pasos['sitio']
        elemento_config = sitio_paso.elemento
        
        print(f"🔧 Processing map configuration...")
        
        # Process map configuration
        map_config = view._process_map_config(registro, elemento_config, rsitio)
        
        print(f"📊 Map config result:")
        print(f"   Enabled: {map_config['enabled']}")
        print(f"   Status: {map_config['status']}")
        print(f"   Coordinates count: {len(map_config['coordinates'])}")
        
        # Print coordinates structure
        for coord_key, coord_data in map_config['coordinates'].items():
            print(f"   {coord_key}:")
            print(f"     lat: {coord_data['lat']}")
            print(f"     lon: {coord_data['lon']}")
            print(f"     label: {coord_data['label']}")
            print(f"     color: {coord_data['color']}")
            print(f"     size: {coord_data['size']}")
        
        # Generate step data structure
        step_data = {
            'title': sitio_paso.title,
            'step_name': 'sitio',
            'registro_id': registro.id,
            'elements': {
                'form': {
                    'url': f'/reg_txtss/{registro.id}/sitio/',
                    'color': 'success'
                },
                'photos': {
                    'enabled': True,
                    'url': f'/reg_txtss/{registro.id}/sitio/photos/',
                    'color': 'success',
                    'count': 0,
                    'required': True,
                    'min_count': 4
                },
                'map': map_config,
                'desfase': {
                    'enabled': False,
                    'distancia': None,
                    'description': '',
                    'color': 'gray'
                }
            },
            'completeness': {
                'color': 'success',
                'is_complete': True,
                'missing_fields': [],
                'total_fields': 5,
                'filled_fields': 5
            }
        }
        
        print(f"\n🎯 Step data structure:")
        print(f"   step.elements.map.enabled: {step_data['elements']['map']['enabled']}")
        print(f"   step.elements.map.coordinates: {list(step_data['elements']['map']['coordinates'].keys())}")
        
        # Test template access patterns
        print(f"\n🧪 Testing template access patterns:")
        
        # Test coord1
        if 'coord1' in step_data['elements']['map']['coordinates']:
            coord1 = step_data['elements']['map']['coordinates']['coord1']
            print(f"   ✅ step.elements.map.coordinates.coord1 exists")
            print(f"      lat: {coord1['lat']}")
            print(f"      lon: {coord1['lon']}")
            print(f"      label: {coord1['label']}")
        else:
            print(f"   ❌ step.elements.map.coordinates.coord1 does not exist")
        
        # Test coord2
        if 'coord2' in step_data['elements']['map']['coordinates']:
            coord2 = step_data['elements']['map']['coordinates']['coord2']
            print(f"   ✅ step.elements.map.coordinates.coord2 exists")
            print(f"      lat: {coord2['lat']}")
            print(f"      lon: {coord2['lon']}")
            print(f"      label: {coord2['label']}")
        else:
            print(f"   ❌ step.elements.map.coordinates.coord2 does not exist")
        
        # Test coord3
        if 'coord3' in step_data['elements']['map']['coordinates']:
            coord3 = step_data['elements']['map']['coordinates']['coord3']
            print(f"   ✅ step.elements.map.coordinates.coord3 exists")
            print(f"      lat: {coord3['lat']}")
            print(f"      lon: {coord3['lon']}")
            print(f"      label: {coord3['label']}")
        else:
            print(f"   ❌ step.elements.map.coordinates.coord3 does not exist")
        
        # Print full structure for debugging
        print(f"\n📋 Full map config structure:")
        print(json.dumps(map_config, indent=2, default=str))
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = debug_map_coordinates()
    if success:
        print("\n🎉 Debug completed successfully!")
    else:
        print("\n💥 Debug failed!")
        sys.exit(1) 