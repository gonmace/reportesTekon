#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.dev')
django.setup()

from django.db import connection

def fix_foreign_key():
    cursor = connection.cursor()
    
    print("Fixing foreign key constraint...")
    
    # Desactivar foreign keys
    cursor.execute('PRAGMA foreign_keys=OFF')
    
    # Crear nueva tabla con la clave foránea correcta
    cursor.execute('''
        CREATE TABLE core_site_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pti_cell_id varchar(100) NULL,
            operator_id varchar(100) NULL,
            name varchar(100) NOT NULL,
            lat_base REAL NULL,
            lon_base REAL NULL,
            alt varchar(100) NULL,
            region varchar(100) NULL,
            comuna varchar(100) NULL,
            is_deleted bool NOT NULL,
            user_id INTEGER NULL REFERENCES users_user(id)
        )
    ''')
    
    # Copiar datos
    cursor.execute('INSERT INTO core_site_new SELECT * FROM core_site')
    
    # Eliminar tabla antigua
    cursor.execute('DROP TABLE core_site')
    
    # Renombrar nueva tabla
    cursor.execute('ALTER TABLE core_site_new RENAME TO core_site')
    
    # Reactivar foreign keys
    cursor.execute('PRAGMA foreign_keys=ON')
    
    print("Foreign key constraint fixed successfully!")

if __name__ == "__main__":
    fix_foreign_key() 