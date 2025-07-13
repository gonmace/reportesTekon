from django.views import View
from django.shortcuts import render

class StepsRegistroView(View):
    def get(self, request, registro_id):
        return render(request, 'pages/steps.html', {'registro_id': registro_id})