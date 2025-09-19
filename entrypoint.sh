#!/bin/sh

# Crear directorio de logs si no existe
mkdir -p /app/logs

# Esperar a que PostgreSQL esté disponible
echo "Esperando a que PostgreSQL esté disponible..."
while ! nc -z construccion-db 5432; do
  echo "PostgreSQL no está listo, esperando..."
  sleep 2
done

echo "PostgreSQL está listo"

# Ejecutar migraciones
echo "Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Crear superusuario si no existe (opcional)
echo "Verificando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"

# Ejecutar Gunicorn con configuración optimizada para producción
echo "Iniciando Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --worker-class gthread \
    --threads 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
