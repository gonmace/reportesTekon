
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls.dashboard')),
    path('', include('core.urls.sitios')),
    # path('', include('registrosWOM.urls')),
    # path('', include('registros.urls')),  # Movido a registros_txtss
    path('txtss/', include('registros_txtss.urls')),
    # path('test/', include('registros_test.urls')),
    path('', include('photos.urls')),
    path('', include('pdf_reports.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
        )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
        )
