from django.contrib import admin
from django.urls import path, include
# urls.py principal
from django.conf import settings
from django.conf.urls.static import static





urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('facturations/', include('facturations.urls')),
    path('', include('inscriptions.urls')),
    path('accounts/', include('utilisateurs.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)