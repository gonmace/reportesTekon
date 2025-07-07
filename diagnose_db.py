#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models.sites import Site
from users.models import User

def diagnose_database():
    print("=== DIAGNÓSTICO DE BASE DE DATOS ===\n")
    
    # Verificar usuarios existentes
    print("1. USUARIOS EXISTENTES:")
    users = User.objects.all()
    for user in users:
        print(f"   ID: {user.id}, Username: {user.username}, Type: {user.user_type}")
    
    print(f"\n   Total usuarios: {users.count()}")
    
    # Verificar sitios
    print("\n2. SITIOS EXISTENTES:")
    sites = Site.objects.all()
    for site in sites:
        print(f"   Site ID: {site.id}, Name: {site.name}, User ID: {site.user_id}")
    
    print(f"\n   Total sitios: {sites.count()}")
    
    # Encontrar sitios con referencias rotas
    print("\n3. SITIOS CON REFERENCIAS ROTAS:")
    broken_sites = []
    for site in sites:
        if not User.objects.filter(id=site.user_id).exists():
            broken_sites.append(site)
            print(f"   Site ID: {site.id}, Name: {site.name}, User ID: {site.user_id} (USUARIO NO EXISTE)")
    
    if not broken_sites:
        print("   No se encontraron sitios con referencias rotas.")
    else:
        print(f"\n   Total sitios con problemas: {len(broken_sites)}")
    
    # Verificar usuarios ITO disponibles
    print("\n4. USUARIOS ITO DISPONIBLES:")
    ito_users = User.objects.filter(user_type=User.ITO)
    for user in ito_users:
        print(f"   ID: {user.id}, Username: {user.username}")
    
    print(f"\n   Total usuarios ITO: {ito_users.count()}")
    
    return broken_sites, ito_users

if __name__ == "__main__":
    broken_sites, ito_users = diagnose_database() 