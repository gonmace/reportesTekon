from django.urls import path, include
from .views import ListPhotosView, UploadPhotosView, UpdatePhotoView, ReorderPhotosView, DeletePhotoView

app_name = "photos"

urlpatterns = [
    path("<str:app_name>/<int:registro_id>/<str:step_name>/photos/", ListPhotosView.as_view(), name="list"),
    path("<str:app_name>/<int:registro_id>/<str:step_name>/photos/upload/", UploadPhotosView.as_view(), name="upload"),
    path("<str:app_name>/<int:registro_id>/<str:step_name>/photos/update/", UpdatePhotoView.as_view(), name="update"),
    path("<str:app_name>/<int:registro_id>/<str:step_name>/photos/reorder/", ReorderPhotosView.as_view(), name="reorder"),
    path("<str:app_name>/<int:registro_id>/<str:step_name>/photos/delete/<int:photo_id>/", DeletePhotoView.as_view(), name="delete"),
]
