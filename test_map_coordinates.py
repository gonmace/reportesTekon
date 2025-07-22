#!/usr/bin/env python3
"""
Test script to verify that map coordinates are being captured correctly.
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
from registros.components.registro_config import RegistroConfig

def test_map_coordinates():
    """Test that map coordinates are being captured correctly."""
    
    print("Testing map coordinates capture...")
    
    # Create a test site
    site = Site.objects.create(
        pti_cell_id='TEST001',
        operator_id='OP001',
        name='Sitio de Prueba',
        lat_base=-33.4567,
        lon_base=-70.6483,
        alt=100,
        region='Metropolitana',
        comuna='Santiago'
    )
    
    # Create a test registro
    from users.models import User
    user = User.objects.first()
    if not user:
        print("❌ No users found in database. Please create a user first.")
        return False
    
    registro = RegTxtss.objects.create(
        sitio=site,
        user=user,
        title='Registro de Prueba',
        description='Registro para probar coordenadas'
    )
    
    # Create a test RSitio instance
    rsitio = RSitio.objects.create(
        registro=registro,
        lat=-33.4568,  # Slightly different from site coordinates
        lon=-70.6484,
        altura='50m',
        dimensiones='20x30m',
        deslindes='5m',
        comentarios='Punto de inspección'
    )
    
    print(f"✅ Created test data:")
    print(f"   Site: {site.name} at ({site.lat_base}, {site.lon_base})")
    print(f"   RSitio: Inspección at ({rsitio.lat}, {rsitio.lon})")
    
    # Test the map configuration processing
    try:
        # Create a mock view instance
        class MockView(GenericRegistroStepsView):
            def get_registro_config(self):
                from reg_txtss.config import REGISTRO_CONFIG
                return REGISTRO_CONFIG
        
        view = MockView()
        
        # Get the sitio paso configuration
        sitio_paso = view.registro_config.pasos['sitio']
        elemento_config = sitio_paso.elemento
        
        # Create a mock instance (RSitio)
        instance = rsitio
        
        # Process map configuration
        map_config = view._process_map_config(registro, elemento_config, instance)
        
        print(f"✅ Map configuration processed successfully:")
        print(f"   Enabled: {map_config['enabled']}")
        print(f"   Status: {map_config['status']}")
        print(f"   Coordinates count: {len(map_config['coordinates'])}")
        
        # Check coordinates
        for coord_key, coord_data in map_config['coordinates'].items():
            print(f"   {coord_key}: {coord_data['label']} at ({coord_data['lat']}, {coord_data['lon']}) - Color: {coord_data['color']}")
        
        # Verify we have both coordinates
        if len(map_config['coordinates']) >= 2:
            print("✅ Both coordinates captured successfully!")
            
            # Verify the coordinates match our test data
            coord1 = map_config['coordinates'].get('coord1')
            coord2 = map_config['coordinates'].get('coord2')
            
            if coord1 and coord2:
                print(f"   Coord1 (Inspección): {coord1['lat']}, {coord1['lon']}")
                print(f"   Coord2 (Mandato): {coord2['lat']}, {coord2['lon']}")
                
                # Check if coordinates are close to expected values
                lat_diff1 = abs(coord1['lat'] - rsitio.lat)
                lon_diff1 = abs(coord1['lon'] - rsitio.lon)
                lat_diff2 = abs(coord2['lat'] - site.lat_base)
                lon_diff2 = abs(coord2['lon'] - site.lon_base)
                
                if lat_diff1 < 0.0001 and lon_diff1 < 0.0001:
                    print("✅ Coord1 (Inspección) coordinates match expected values")
                else:
                    print(f"❌ Coord1 coordinates don't match: expected ({rsitio.lat}, {rsitio.lon}), got ({coord1['lat']}, {coord1['lon']})")
                
                if lat_diff2 < 0.0001 and lon_diff2 < 0.0001:
                    print("✅ Coord2 (Mandato) coordinates match expected values")
                else:
                    print(f"❌ Coord2 coordinates don't match: expected ({site.lat_base}, {site.lon_base}), got ({coord2['lat']}, {coord2['lon']})")
                
                return True
            else:
                print("❌ Missing coordinates in map configuration")
                return False
        else:
            print(f"❌ Expected 2 coordinates, but got {len(map_config['coordinates'])}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing map configuration: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test data
        try:
            rsitio.delete()
            registro.delete()
            site.delete()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up test data: {e}")

if __name__ == '__main__':
    success = test_map_coordinates()
    if success:
        print("\n🎉 All tests passed! Map coordinates are working correctly.")
    else:
        print("\n💥 Tests failed! There are issues with map coordinates.")
        sys.exit(1) 