from .base import ElementoRegistro
from .elementos import SubElementoTable, SubElementoMap, SubElementoPhotos, SubElementoChart, SubElementoDocuments


class SubElementoFactory:
    """
    Factory para crear sub-elementos específicos.
    """
    SUB_ELEMENTOS = {
        'table': SubElementoTable,
        'map': SubElementoMap,
        'photos': SubElementoPhotos,
        'chart': SubElementoChart,
        'documents': SubElementoDocuments,
    }

    @classmethod
    def create_sub_elemento(cls, tipo, elemento_padre):
        """
        Crea un sub-elemento específico.
        
        Args:
            tipo (str): Tipo de sub-elemento ('table', 'map', 'photos', 'chart', 'documents')
            elemento_padre: Instancia del elemento padre
            
        Returns:
            SubElemento: Instancia del sub-elemento específico
        """
        if tipo not in cls.SUB_ELEMENTOS:
            raise ValueError(f"Tipo de sub-elemento '{tipo}' no válido. Tipos disponibles: {list(cls.SUB_ELEMENTOS.keys())}")
        
        sub_elemento_class = cls.SUB_ELEMENTOS[tipo]
        return sub_elemento_class(elemento_padre)

    @classmethod
    def get_sub_elemento_info(cls, tipo):
        """
        Obtiene información sobre un tipo de sub-elemento.
        
        Args:
            tipo (str): Tipo de sub-elemento
            
        Returns:
            dict: Información del sub-elemento
        """
        if tipo not in cls.SUB_ELEMENTOS:
            return None
        
        sub_elemento_class = cls.SUB_ELEMENTOS[tipo]
        return {
            'nombre': sub_elemento_class.__name__,
            'tipo': sub_elemento_class.tipo,
            'template': sub_elemento_class.template_name,
        }

    @classmethod
    def get_available_tipos(cls):
        """
        Obtiene la lista de tipos de sub-elementos disponibles.
        
        Returns:
            list: Lista de tipos disponibles
        """
        return list(cls.SUB_ELEMENTOS.keys())


class ElementoFactory:
    """
    Factory para crear elementos específicos con sub-elementos.
    """
    @classmethod
    def create_elemento(cls, registro, model=None, form_class=None, sub_elementos=None):
        """
        Crea un elemento específico con sub-elementos opcionales.
        
        Args:
            registro: Instancia del registro
            model: Modelo específico para el elemento
            form_class: Clase de formulario específica
            sub_elementos: Lista de tipos de sub-elementos a agregar
            
        Returns:
            ElementoRegistro: Instancia del elemento específico
        """
        # Crear una clase dinámica que herede de ElementoRegistro
        class ElementoEspecifico(ElementoRegistro):
            pass
        
        # Configurar modelo y formulario
        if model:
            ElementoEspecifico.model = model
        if form_class:
            ElementoEspecifico.form_class = form_class
        
        # Configurar sub-elementos
        if sub_elementos:
            ElementoEspecifico.sub_elementos = {}
            for tipo in sub_elementos:
                ElementoEspecifico.sub_elementos[tipo] = SubElementoFactory.SUB_ELEMENTOS.get(tipo)
        
        # Crear instancia
        elemento = ElementoEspecifico(registro)
        
        return elemento

    @classmethod
    def validate_registro(cls, registro):
        """
        Valida que el registro sea válido para crear elementos.
        
        Args:
            registro: Instancia del registro
            
        Returns:
            bool: True si es válido, False en caso contrario
        """
        # Validación básica - verificar que tenga atributos necesarios
        if not hasattr(registro, 'id'):
            return False
        
        if hasattr(registro, 'is_active') and not registro.is_active:
            return False
        
        return True 