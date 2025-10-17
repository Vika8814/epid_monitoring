# monitoring_system/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api import views

# Створюємо роутер, який автоматично згенерує URL для наших ViewSets
router = routers.DefaultRouter()
router.register(r'institutions', views.InstitutionViewSet)
router.register(r'visits', views.VisitViewSet)
router.register(r'symptoms', views.SymptomViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # <-- ДОДАНО. Всі API будуть за адресою /api/...
]