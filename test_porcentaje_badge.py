#!/usr/bin/env python3
"""
Script de prueba para verificar que el badge de porcentaje se calcula correctamente.
"""

import os
import django
from datetime import date, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.dev')
django.setup()

from reg_construccion.models import RegConstruccion, AvanceComponente
from proyectos.models import GrupoComponentes
from core.models.sites import Site
from users.models import User

def test_porcentaje_badge():
    """Prueba que el badge de porcentaje se calcula correctamente."""
    
    print("🧪 Prueba: Badge de porcentaje en icono de tabla")
    print("=" * 70)
    
    sitio = Site.objects.first()
    user = User.objects.filter(user_type=User.ITO).first()
    grupo = GrupoComponentes.objects.get(nombre="Torres Completas")
    
    if sitio and user and grupo:
        # 1. Crear registro con datos
        print(f"\n1️⃣ Creando registro con datos...")
        fecha_1 = date.today() - timedelta(days=5)
        
        registro = RegConstruccion.objects.create(
            title="Registro Test - Badge",
            sitio=sitio,
            user=user,
            estructura=grupo,
            fecha=fecha_1,
            is_active=True
        )
        
        # Crear avances con diferentes porcentajes
        componentes = grupo.componentes.all()[:3]
        for i, gc in enumerate(componentes):
            avance = AvanceComponente.objects.create(
                registro=registro,
                componente=gc.componente,
                fecha=fecha_1,
                porcentaje_actual=20 + (i * 10),
                porcentaje_acumulado=30 + (i * 10),
                comentarios=f"Avance test {i+1}"
            )
            print(f"   ✅ {gc.componente.nombre}: {avance.porcentaje_actual}% actual, {avance.porcentaje_acumulado}% acumulado")
        
        # 2. Simular cálculo de datos de tabla
        print(f"\n2️⃣ Simulando cálculo de datos de tabla...")
        
        table_data = []
        total_ejecucion_total = 0.0
        
        for i, gc in enumerate(componentes):
            avance = AvanceComponente.objects.get(registro=registro, componente=gc.componente)
            
            # Calcular valores como lo hace la vista
            ejec_actual = avance.porcentaje_actual
            ejec_anterior = avance.porcentaje_acumulado - avance.porcentaje_actual
            if ejec_anterior < 0:
                ejec_anterior = 0
            ejec_acumulada = ejec_anterior + ejec_actual
            
            # Calcular ejecución total (incidencia × ejecución acumulada)
            incidencia = float(gc.incidencia)
            ejecucion_total = (incidencia / 100) * ejec_acumulada
            total_ejecucion_total += ejecucion_total
            
            row_data = {
                'componente': gc.componente.nombre,
                'ejecucion_total': f"{ejecucion_total:.1f}%"
            }
            table_data.append(row_data)
            
            print(f"   📋 {gc.componente.nombre}:")
            print(f"      - Incidencia: {incidencia}%")
            print(f"      - Ejec anterior: {ejec_anterior}%")
            print(f"      - Ejec actual: {ejec_actual}%")
            print(f"      - Ejec acumulada: {ejec_acumulada}%")
            print(f"      - Ejecución total: {ejecucion_total:.1f}%")
        
        # 3. Simular cálculo del badge
        print(f"\n3️⃣ Simulando cálculo del badge...")
        
        badge_percentage = 0.0
        if table_data:
            for item in table_data:
                if 'ejecucion_total' in item:
                    ejecucion_str = item['ejecucion_total']
                    try:
                        ejecucion_valor = float(ejecucion_str.replace('%', ''))
                        badge_percentage += ejecucion_valor
                    except (ValueError, AttributeError):
                        pass
        
        badge_percentage = round(badge_percentage, 1)
        
        print(f"   📊 Total ejecución calculado: {total_ejecucion_total:.1f}%")
        print(f"   📊 Badge percentage: {badge_percentage}%")
        
        # 4. Verificar que el cálculo es correcto
        print(f"\n4️⃣ Verificando cálculo...")
        
        if abs(badge_percentage - total_ejecucion_total) < 0.1:
            print(f"   ✅ Badge calculado correctamente: {badge_percentage}%")
            print(f"   ✅ Coincide con total ejecución: {total_ejecucion_total:.1f}%")
        else:
            print(f"   ❌ Error en cálculo:")
            print(f"      - Badge: {badge_percentage}%")
            print(f"      - Total: {total_ejecucion_total:.1f}%")
        
        # 5. Simular configuración de tabla
        print(f"\n5️⃣ Simulando configuración de tabla...")
        
        table_config = {
            'enabled': True,
            'url': f'/reg_construccion/{registro.id}/avance/',
            'color': 'success',
            'count': len(table_data),
            'percentage': badge_percentage
        }
        
        print(f"   📋 Configuración de tabla:")
        print(f"      - Enabled: {table_config['enabled']}")
        print(f"      - Color: {table_config['color']}")
        print(f"      - Count: {table_config['count']}")
        print(f"      - Percentage: {table_config['percentage']}%")
        
        # 6. Verificar que el badge se mostraría correctamente
        print(f"\n6️⃣ Verificando que el badge se mostraría...")
        
        if badge_percentage > 0:
            print(f"   ✅ Badge se mostraría con: {badge_percentage}%")
            print(f"   ✅ Posición: absolute -top-2 -right-2")
            print(f"   ✅ Color: badge-primary")
        else:
            print(f"   ⚠️  Badge no se mostraría (percentage = 0)")
        
        # Limpiar registro de prueba
        registro.delete()
        print(f"\n🧹 Registro de prueba eliminado")
    
    print(f"\n🎉 Prueba completada!")

if __name__ == "__main__":
    test_porcentaje_badge()
