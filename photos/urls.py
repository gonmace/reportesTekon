from django.urls import path, include
from .views import ListPhotosView, UploadPhotosView, UpdatePhotoView, ReorderPhotosView, DeletePhotoView

app_name = "photos"

urlpatterns = [
    path("<int:registro_id>/<str:title>/photos/", ListPhotosView.as_view(), name="list"),
    path("<int:registro_id>/<str:title>/photos/upload/", UploadPhotosView.as_view(), name="upload"),
    path("<int:registro_id>/<str:title>/photos/update/", UpdatePhotoView.as_view(), name="update"),
    path("<int:registro_id>/<str:title>/photos/reorder/", ReorderPhotosView.as_view(), name="reorder"),
    path("<int:registro_id>/<str:title>/photos/delete/<int:photo_id>/", DeletePhotoView.as_view(), name="delete"),
]
