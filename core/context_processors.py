from core.menu.menu_builder import MenuBuilder
import os


def menu_context(request):
    return {
        'menu_items': MenuBuilder.get_menu(request.user, request.path, request),
        'parent_system_url': os.getenv('PARENT_SYSTEM_URL', ''),
    }
