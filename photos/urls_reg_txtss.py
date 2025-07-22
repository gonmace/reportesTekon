from django.urls import path
from .views import ListPhotosView, UploadPhotosView, UpdatePhotoView, ReorderPhotosView, DeletePhotoView

app_name = "photos"

urlpatterns = [
    # Rutas para cuando se incluye desde reg_txtss (sin app_name)
    path('', ListPhotosView.as_view(), name="list"),
    path('upload/', UploadPhotosView.as_view(), name="upload"),
    path('update/', UpdatePhotoView.as_view(), name="update"),
    path('reorder/', ReorderPhotosView.as_view(), name="reorder"),
    path('delete/<int:photo_id>/', DeletePhotoView.as_view(), name="delete"),
] 