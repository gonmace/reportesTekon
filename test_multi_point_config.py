#!/usr/bin/env python3
"""
Test script to verify the new parameter structure for create_multi_point_map_config.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registros.config import create_multi_point_map_config
from core.models.sites import Site

def test_new_parameter_structure():
    """Test the new parameter structure for create_multi_point_map_config."""
    
    print("Testing new parameter structure for create_multi_point_map_config...")
    
    # Test with the new parameter structure
    try:
        config = create_multi_point_map_config(
            model_class1='current',
            lat1='lat',
            lon1='lon', 
            name1='Inspección',
            model_class2=Site,
            lat2='lat_base',
            lon2='lon_base', 
            name2='Mandato',
            second_model_relation_field='registro_txtss',
            descripcion_distancia='Desfase Mandato-Inspección',
            zoom=15,
            icon1_color='red',
            icon1_size='large',
            icon1_type='marker',
            icon2_color='blue',
            icon2_size='normal',
            icon2_type='marker'
        )
        
        print("✅ Successfully created configuration with new parameter structure")
        print(f"   Config type: {type(config)}")
        print(f"   Config tipo: {config.tipo}")
        print(f"   Map config: {config.config}")
        
        # Verify the configuration structure
        map_config = config.config
        assert map_config['lat_field'] == 'lat'
        assert map_config['lon_field'] == 'lon'
        assert map_config['name_field'] == 'Inspección'
        assert map_config['zoom'] == 15
        assert map_config['type'] == 'multi_point'
        
        # Verify icon configuration
        icon_config = map_config['icon_config']
        assert icon_config['color'] == 'red'
        assert icon_config['size'] == 'large'
        assert icon_config['type'] == 'marker'
        
        # Verify second model configuration
        second_model = map_config['second_model']
        assert second_model['model_class'] == Site
        assert second_model['lat_field'] == 'lat_base'
        assert second_model['lon_field'] == 'lon_base'
        assert second_model['name_field'] == 'Mandato'
        assert second_model['relation_field'] == 'registro_txtss'
        
        # Verify second model icon configuration
        second_icon_config = second_model['icon_config']
        assert second_icon_config['color'] == 'blue'
        assert second_icon_config['size'] == 'normal'
        assert second_icon_config['type'] == 'marker'
        
        print("✅ All configuration values verified correctly")
        
    except Exception as e:
        print(f"❌ Error creating configuration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_new_parameter_structure()
    if success:
        print("\n🎉 All tests passed! The new parameter structure is working correctly.")
    else:
        print("\n💥 Tests failed! Please check the implementation.")
        sys.exit(1) 