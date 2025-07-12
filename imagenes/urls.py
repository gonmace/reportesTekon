from django.urls import path, include
from .views import ListImagenesView, UploadImagenesView, UpdateImagenView, ReorderImagenesView, DeleteImagenView

app_name = "imagenes"

urlpatterns = [
    path("imagenes/", ListImagenesView.as_view(), name="list"),
    path("imagenes/upload/", UploadImagenesView.as_view(), name="upload"),
    path("imagenes/update/", UpdateImagenView.as_view(), name="update"),
    path("imagenes/reorder/", ReorderImagenesView.as_view(), name="reorder"),
    path("imagenes/delete/<int:imagen_id>/", DeleteImagenView.as_view(), name="delete"),
]
