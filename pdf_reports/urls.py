from django.urls import path
from .views import TxtssPDFView, preview_registro_individual

app_name = 'pdf_reports'

urlpatterns = [
    path('pdf/<int:registro_id>/', TxtssPDFView.as_view(), name='txtss_pdf'),
    path('preview/<int:registro_id>/', preview_registro_individual, name='preview_registro_individual'),
]