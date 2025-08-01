from django.apps import AppConfig


class ProyectosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectos'
    
    def ready(self):
        """Registrar signals cuando la app está lista"""
        import proyectos.signals