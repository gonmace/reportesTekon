from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View

@login_required
def debug_form_view(request):
    """Vista para debug de formularios."""
    return render(request, 'debug_form.html')

@csrf_exempt
class DebugFormView(View):
    """Vista para recibir formularios de prueba."""
    
    def post(self, request):
        """Maneja peticiones POST de formularios de prueba."""
        try:
            # Obtener datos del formulario
            form_data = request.POST.dict()
            files = request.FILES
            
            print(f"📝 Datos recibidos en debug: {form_data}")
            print(f"📁 Archivos recibidos: {files}")
            
            return JsonResponse({
                'success': True,
                'message': 'Formulario recibido correctamente',
                'data': form_data,
                'files_count': len(files)
            })
            
        except Exception as e:
            print(f"❌ Error en debug form: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    def get(self, request):
        """Maneja peticiones GET."""
        return JsonResponse({
            'success': True,
            'message': 'Debug endpoint funcionando',
            'method': 'GET'
        }) 