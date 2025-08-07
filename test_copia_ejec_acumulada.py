#!/usr/bin/env python3
"""
Script de prueba para verificar que se copia EJEC ACUMULADA a EJEC ANTERIOR.
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

def test_copia_ejec_acumulada():
    """Prueba que se copia EJEC ACUMULADA a EJEC ANTERIOR."""
    
    print("🧪 Prueba: Copia EJEC ACUMULADA a EJEC ANTERIOR")
    print("=" * 70)
    
    sitio = Site.objects.first()
    user = User.objects.filter(user_type=User.ITO).first()
    grupo = GrupoComponentes.objects.get(nombre="Torres Completas")
    
    if sitio and user and grupo:
        # 1. Crear primera fecha con datos
        print(f"\n1️⃣ Creando primera fecha con datos...")
        fecha_1 = date.today() - timedelta(days=10)
        
        registro_1 = RegConstruccion.objects.create(
            title="Primera Fecha - Test",
            sitio=sitio,
            user=user,
            estructura=grupo,
            fecha=fecha_1,
            is_active=True
        )
        
        # Crear avances para la primera fecha
        componentes = grupo.componentes.all()[:3]
        for i, gc in enumerate(componentes):
            avance = AvanceComponente.objects.create(
                registro=registro_1,
                componente=gc.componente,
                fecha=fecha_1,
                porcentaje_actual=20 + (i * 5),
                porcentaje_acumulado=30 + (i * 5),  # EJEC ACUMULADA
                comentarios=f"Avance primera fecha {i+1}"
            )
            print(f"   ✅ {gc.componente.nombre}: {avance.porcentaje_actual}% actual, {avance.porcentaje_acumulado}% acumulado")
        
        # 2. Simular creación de nueva fecha
        print(f"\n2️⃣ Simulando creación de nueva fecha...")
        fecha_2 = date.today() - timedelta(days=5)
        
        registro_2 = RegConstruccion.objects.create(
            title="Segunda Fecha - Test",
            sitio=sitio,
            user=user,
            estructura=grupo,
            fecha=fecha_2,
            is_active=True
        )
        
        # 3. Simular la lógica de copia
        print(f"\n3️⃣ Simulando lógica de copia...")
        
        # Buscar registro anterior
        registro_anterior = RegConstruccion.objects.filter(
            sitio=sitio,
            user=user,
            is_active=True,
            is_deleted=False,
            estructura__isnull=False
        ).exclude(
            id=registro_2.id
        ).order_by('-fecha').first()
        
        if registro_anterior:
            print(f"📋 Registro anterior encontrado: {registro_anterior.title}")
            
            # Obtener avances del registro anterior
            avances_anteriores = AvanceComponente.objects.filter(
                registro=registro_anterior
            ).select_related('componente')
            
            # Crear avances para la nueva fecha copiando EJEC ACUMULADA
            for avance_anterior in avances_anteriores:
                nuevo_avance = AvanceComponente.objects.create(
                    registro=registro_2,
                    componente=avance_anterior.componente,
                    fecha=date.today(),
                    porcentaje_actual=0,  # Ejecución actual en 0
                    porcentaje_acumulado=avance_anterior.porcentaje_acumulado,  # Copiar acumulado anterior
                    comentarios=f"Copiado desde {registro_anterior.fecha.strftime('%d/%m/%Y')}"
                )
                print(f"   ✅ Creado avance para: {avance_anterior.componente.nombre}")
                print(f"      - Ejec anterior: {avance_anterior.porcentaje_acumulado}% (copiada desde acumulada)")
                print(f"      - Ejec actual: 0% (nueva fecha)")
                print(f"      - Ejec acumulada: {avance_anterior.porcentaje_acumulado}% (mantenida)")
        
        # 4. Verificar resultados
        print(f"\n4️⃣ Verificando resultados...")
        
        avances_nuevos = AvanceComponente.objects.filter(registro=registro_2)
        print(f"   - Avances en nueva fecha: {avances_nuevos.count()}")
        
        for avance in avances_nuevos:
            # Calcular ejec_anterior (como lo hace la vista)
            ejec_anterior = avance.porcentaje_acumulado - avance.porcentaje_actual
            if ejec_anterior < 0:
                ejec_anterior = 0
            
            print(f"   📋 {avance.componente.nombre}:")
            print(f"      - Ejec anterior calculada: {ejec_anterior}%")
            print(f"      - Ejec actual: {avance.porcentaje_actual}%")
            print(f"      - Ejec acumulada: {avance.porcentaje_acumulado}%")
            
            # Verificar que ejec_anterior = ejec_acumulada (porque actual=0)
            if ejec_anterior == avance.porcentaje_acumulado:
                print(f"      ✅ Correcto: EJEC ACUMULADA copiada a EJEC ANTERIOR")
            else:
                print(f"      ❌ Error: EJEC ANTERIOR no coincide con ACUMULADA")
        
        # 5. Verificar que los valores son correctos
        print(f"\n5️⃣ Verificando valores correctos...")
        
        for i, gc in enumerate(componentes):
            avance_1 = AvanceComponente.objects.get(registro=registro_1, componente=gc.componente)
            avance_2 = AvanceComponente.objects.get(registro=registro_2, componente=gc.componente)
            
            valor_acumulado_anterior = avance_1.porcentaje_acumulado
            valor_anterior_nuevo = avance_2.porcentaje_acumulado - avance_2.porcentaje_actual
            
            if valor_anterior_nuevo < 0:
                valor_anterior_nuevo = 0
            
            if valor_anterior_nuevo == valor_acumulado_anterior:
                print(f"   ✅ {gc.componente.nombre}: EJEC ACUMULADA copiada correctamente")
                print(f"      - Anterior: {valor_acumulado_anterior}%")
                print(f"      - Nueva fecha: {valor_anterior_nuevo}%")
            else:
                print(f"   ❌ {gc.componente.nombre}: Error en copia")
                print(f"      - Anterior: {valor_acumulado_anterior}%")
                print(f"      - Nueva fecha: {valor_anterior_nuevo}%")
        
        # Limpiar registros de prueba
        registro_2.delete()
        registro_1.delete()
        print(f"\n🧹 Registros de prueba eliminados")
    
    print(f"\n🎉 Prueba completada!")

if __name__ == "__main__":
    test_copia_ejec_acumulada()
