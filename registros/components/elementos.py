from django.shortcuts import render


class SubElemento:
    """
    Clase base para sub-elementos (fotos, mapas, tablas, etc.)
    que se pueden agregar a un ElementoRegistro.
    """
    tipo = None
    template_name = None
    elemento_padre = None

    def __init__(self, elemento_padre):
        self.elemento_padre = elemento_padre

    def get_data(self):
        """Obtiene los datos específicos del sub-elemento."""
        return {}

    def render_template(self, request, context=None):
        """Renderiza el template del sub-elemento."""
        if context is None:
            context = {}
        
        context.update({
            'elemento_padre': self.elemento_padre,
            'sub_elemento': self,
            'data': self.get_data(),
        })
        
        return render(request, self.template_name, context)

    def to_dict(self):
        """Convierte el sub-elemento a diccionario."""
        return {
            'tipo': self.tipo,
            'data': self.get_data(),
        }


class SubElementoTable(SubElemento):
    """
    Sub-elemento para tablas de datos.
    """
    tipo = 'table'
    template_name = 'registros/templates/components/sub_elemento_table.html'

    def get_data(self):
        """Obtiene los datos para la tabla."""
        if hasattr(self.elemento_padre, 'model') and self.elemento_padre.model:
            queryset = self.elemento_padre.get_queryset()
            if queryset:
                return queryset.all()
        return []


class SubElementoMap(SubElemento):
    """
    Sub-elemento para mapas.
    """
    tipo = 'map'
    template_name = 'registros/templates/components/sub_elemento_map.html'

    def get_data(self):
        """Obtiene las coordenadas para el mapa."""
        if self.elemento_padre.instance and hasattr(self.elemento_padre.instance, 'lat') and hasattr(self.elemento_padre.instance, 'lon'):
            return {
                'lat': self.elemento_padre.instance.lat,
                'lon': self.elemento_padre.instance.lon,
                'label': self.elemento_padre.tipo,
                'color': '#3B82F6',
            }
        return None


class SubElementoPhotos(SubElemento):
    """
    Sub-elemento para galerías de fotos.
    """
    tipo = 'photos'
    template_name = 'registros/templates/components/sub_elemento_photos.html'

    def get_data(self):
        """Obtiene las fotos asociadas."""
        # Aquí implementarías la lógica para obtener fotos
        # Por ejemplo, buscar fotos relacionadas con el elemento padre
        if hasattr(self.elemento_padre, 'model') and self.elemento_padre.model:
            # Buscar fotos relacionadas con el modelo del elemento padre
            return []
        return []


class SubElementoChart(SubElemento):
    """
    Sub-elemento para gráficos.
    """
    tipo = 'chart'
    template_name = 'registros/templates/components/sub_elemento_chart.html'

    def get_data(self):
        """Obtiene los datos para el gráfico."""
        # Implementar lógica específica para obtener datos del gráfico
        return {
            'labels': [],
            'data': [],
            'type': 'bar',  # o 'line', 'pie', etc.
        }


class SubElementoDocuments(SubElemento):
    """
    Sub-elemento para documentos.
    """
    tipo = 'documents'
    template_name = 'registros/templates/components/sub_elemento_documents.html'

    def get_data(self):
        """Obtiene los documentos asociados."""
        # Implementar lógica para obtener documentos
        return [] 