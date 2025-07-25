
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls.dashboard')),
    path('', include('core.urls.sitios')),
    path('reg_txtss/', include('reg_txtss.urls')),
    path('reg_visita/', include('reg_visita.urls')),
    path('', include('photos.urls')),
    path('', include('pdf_reports.urls')),
    path('api/', include('core.urls.api')),
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
