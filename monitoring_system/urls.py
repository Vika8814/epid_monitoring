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
router.register(r'chatrooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # <-- ДОДАНО. Всі API будуть за адресою /api/...
    path('api/statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('api/sir_modeling/', views.SIRModelingView.as_view(), name='sir_modeling'),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]