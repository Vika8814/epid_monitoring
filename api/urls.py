# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views  # Імпортуємо всі наші views з api/views.py

# --- 1. Роутер для "бази даних" (моделей) ---
# Це автоматично створює URL-и для ваших моделей (GET, POST, PUT, DELETE)1          
router = DefaultRouter()
router.register(r'institutions', views.InstitutionViewSet, basename='institution')
router.register(r'patients', views.PatientViewSet, basename='patient')
router.register(r'visits', views.VisitViewSet, basename='visit')
router.register(r'symptoms', views.SymptomViewSet, basename='symptom')
router.register(r'chatrooms', views.ChatRoomViewSet, basename='chatroom')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'reports', views.ReportViewSet, basename='report') # Для завантаження файлів

# --- 2. Головний список URL-адрес ---
urlpatterns = [
    # --- URL-и для Реєстрації, Входу, Виходу ---
    # Це підключить /api/auth/login/, /api/auth/logout/ і т.д.
    path('auth/', include('dj_rest_auth.urls')),
    
    # Це підключить /api/auth/registration/
    path('auth/registration/', include('dj_rest_auth.registration.urls')),
    
    
    # --- Спеціальні URL-и ---
    # (Для ваших кастомних APIView)
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    path('sir_modeling/', views.SIRModelingView.as_view(), name='sir_modeling'),
    path('quick-report/', views.QuickReportView.as_view(), name='quick-report'), # Для PDF-звіту
    path('search/', views.SearchView.as_view(), name='search'),
    
    
    # --- URL-и з Роутера ---
    # Це має бути в кінці, щоб підключити всі URL-и моделей
    # (напр. /api/visits/, /api/reports/)
    path('', include(router.urls)),
]