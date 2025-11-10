# monitoring_system/urls.py

from django.contrib import admin
from django.urls import path, include  # <-- Вам потрібен 'include'
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Цей рядок каже Django:
    # "Для будь-якого шляху, що починається з 'api/',
    # шукай інструкції у файлі 'api.urls'"
    path('api/', include('api.urls')), 
]

# Це потрібно для обслуговування завантажених файлів (напр. звітів)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)