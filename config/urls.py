from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', include('pages.urls')), 
    path('', include('listings.urls')),
    path('realtors/', include('realtors.urls')),
    path('contacts/', include('contacts.urls')), 
    path('accounts/', include('accounts.urls')),
    path('', include('prediction.urls')),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

