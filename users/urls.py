from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    # Aquí se pueden agregar más URLs de autenticación si es necesario
]
