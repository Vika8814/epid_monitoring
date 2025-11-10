# api/views.py

# --- Імпорти Django ---
from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import TruncDay
from django.http import HttpResponse  # <-- ДОДАЙТЕ ЦЕЙ ІМПОРТ
from django.contrib.auth import get_user_model

# --- Імпорти Rest Framework ---
# api/views.py
from rest_framework import viewsets, serializers, permissions, parsers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

# --- Імпорти dj-rest-auth ---
from dj_rest_auth.views import LoginView as RestAuthLoginView
from dj_rest_auth.views import LogoutView as RestAuthLogoutView
from dj_rest_auth.registration.views import RegisterView as RestAuthRegisterView

# --- Імпорти сторонніх бібліотек ---
import numpy as np
# --- ДОДАЙТЕ ІМПОРТИ ДЛЯ PDF ---
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# --- Локальні імпорти (моделі та серіалізатори) ---
from .models import (
    Institution, Visit, Symptom, ChatRoom, Message, Patient, Report
)
from .serializers import (
    InstitutionSerializer, VisitSerializer, SymptomSerializer,
    ChatRoomSerializer, MessageSerializer, PatientSerializer,
    ReportSerializer, UserDetailSerializer
)

# --- ДОДАЙТЕ РЕЄСТРАЦІЮ ШРИФТУ ---
# (Це потрібно для кирилиці у PDF)
try:
    pdfmetrics.registerFont(TTFont('FreeSans', '/usr/share/fonts/truetype/freefont/FreeSans.ttf'))
except IOError:
    # Це може бути інший шлях у вашому Docker-контейнері
    print("ПОПЕРЕДЖЖЕННЯ: Шрифт FreeSans не знайдено. PDF може мати проблеми з кирилицею.")


# --- ViewSets для простого отримання даних (GET) ---

class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [AllowAny]

class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if hasattr(user, 'role') and user.role in ['Аналітик', 'Адмін']:
                return Visit.objects.all().order_by('-visit_date')
            elif hasattr(user, 'institution') and user.institution:
                return Visit.objects.filter(institution=user.institution).order_by('-visit_date')
        return Visit.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'institution') and self.request.user.institution:
            serializer.save(
                doctor=self.request.user,
                institution=self.request.user.institution
            )
        else:
            raise serializers.ValidationError("Користувач не прив'язаний до закладу.")

class SymptomViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer
    permission_classes = [AllowAny]

# --- API для сторінки статистики (GET) ---

class StatisticsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        disease_dynamics = (
            Visit.objects
            .annotate(day=TruncDay('visit_date'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        disease_distribution = (
            Visit.objects
            .values('symptoms__category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        data = {
            'disease_dynamics': list(disease_dynamics),
            'disease_distribution': list(disease_distribution)
        }
        return Response(data)

# --- API для SIR-моделювання (POST) ---

class SIRModelingView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        N = int(request.data.get('population', 1000))
        I0 = int(request.data.get('initial_infected', 1))
        R0 = int(request.data.get('initial_recovered', 0))
        beta = float(request.data.get('beta', 0.2))
        gamma = float(request.data.get('gamma', 0.1))
        days = int(request.data.get('days', 160))
        S0 = N - I0 - R0
        S, I, R = [S0], [I0], [R0]
        for t in range(days - 1):
            new_infections = (beta * S[-1] * I[-1]) / N if N > 0 else 0
            new_recoveries = gamma * I[-1]
            S_next = S[-1] - new_infections
            I_next = I[-1] + new_infections - new_recoveries
            R_next = R[-1] + new_recoveries
            S.append(max(0, S_next))
            I.append(max(0, I_next))
            R.append(max(0, R_next))
        results = {
            'days': list(range(days)),
            'susceptible': S,
            'infected': I,
            'recovered': R
        }
        return Response(results)

# --- API для Чату (GET та POST) ---

class ChatRoomViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user_institution = getattr(self.request.user, 'institution', None)
        if user_institution:
            return ChatRoom.objects.filter(participants=user_institution)
        return ChatRoom.objects.none()

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        room_id = self.request.query_params.get('room')
        if room_id:
            user_institution = getattr(self.request.user, 'institution', None)
            if user_institution and ChatRoom.objects.filter(id=room_id, participants=user_institution).exists():
                return Message.objects.filter(room_id=room_id)
        return Message.objects.none()

    def perform_create(self, serializer):
        room = serializer.validated_data.get('room')
        user_institution = getattr(self.request.user, 'institution', None)
        if user_institution and room.participants.filter(id=user_institution.id).exists():
            serializer.save(sender=self.request.user)
        else:
            raise PermissionDenied("Ви не є учасником цієї чат-кімнати.")

# --- API для Завантаження Звітів (POST) ---

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        return self.request.user.reports.all().order_by('-uploaded_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
# --- ДОДАЙТЕ ВІДСУТНІЙ КЛАС ДЛЯ PDF-ЗВІТУ ---
class QuickReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 1. Створюємо відповідь типу PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="quick_report.pdf"'

        # 2. Створюємо "полотно" PDF
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        p.setFont('FreeSans', 12)

        # --- 3. ЗБИРАЄМО ДАНІ ---
        total_visits = Visit.objects.count()
        total_patients = Patient.objects.count()
        
        most_common_symptom_data = Visit.objects.values('symptoms__category') \
                                              .annotate(count=Count('symptoms__category')) \
                                              .order_by('-count') \
                                              .first()
        
        if most_common_symptom_data and most_common_symptom_data['symptoms__category']:
            most_common_symptom = f"{most_common_symptom_data['symptoms__category']} ({most_common_symptom_data['count']} випадків)"
        else:
            most_common_symptom = "Немає даних"

        latest_visits = Visit.objects.all().order_by('-visit_date')[:5]

        
        # --- 4. МАЛЮЄМО ДАНІ НА PDF ---
        y = height - 100 

        p.setFont('FreeSans', 16)
        p.drawString(100, y, "Швидкий звіт: Епідеміологічна ситуація")
        y -= 20
        p.drawString(100, y, "---------------------------------------------")
        y -= 30

        p.setFont('FreeSans', 12)
        p.drawString(100, y, f"Загальна кількість візитів: {total_visits}")
        y -= 20
        p.drawString(100, y, f"Загальна кількість пацієнтів: {total_patients}")
        y -= 20
        p.drawString(100, y, f"Найпоширеніша категорія симптомів: {most_common_symptom}")
        y -= 40

        p.setFont('FreeSans', 14)
        p.drawString(100, y, "Останні 5 візитів:")
        y -= 25
        
        p.setFont('FreeSans', 10)
        for visit in latest_visits:
            #
            # --- ОСЬ ТУТ БУЛА ПОМИЛКА ВІДСТУПУ ---
            #
            visit_date = visit.visit_date.strftime('%Y-%m-%d')
            # Цей рядок тепер має правильний відступ (він всередині циклу for)
            patient_name = str(visit.patient) if visit.patient else "Невідомий пацієнт"
            
            p.drawString(120, y, f"• Дата: {visit_date} - Пацієнт: {patient_name}")
            y -= 15

        # 5. Закриваємо та зберігаємо PDF
        p.showPage()
        p.save()

        return response


class SearchView(APIView):
    """
    API для глобального пошуку.
    Приймає GET-запит з параметром ?q=...
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        print(f"--- [SEARCH] Отримано запит: {query} ---") # <-- ДЛЯ ДІАГНОСТИКИ

        if not query:
            return Response({
                'patients': [],
                'institutions': []
            })
            
        User = get_user_model()

        # --- 1. Шукаємо Користувачів (User) ---
        user_results = User.objects.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query)      
        ).distinct()[:10]
        
        print(f"--- [SEARCH] Знайдено користувачів: {user_results.count()} ---")

        # --- 2. Шукаємо заклади ---
        institution_results = Institution.objects.filter(
            Q(name__icontains=query)
        ).distinct()[:10]
        
        print(f"--- [SEARCH] Знайдено закладів: {institution_results.count()} ---")

        # --- 3. Серіалізуємо дані ---
        patient_data = UserDetailSerializer(user_results, many=True).data 
        institution_data = InstitutionSerializer(institution_results, many=True).data

        # --- 4. Повертаємо відповідь ---
        response_data = {
            'patients': patient_data, 
            'institutions': institution_data
        }
        print(f"--- [SEARCH] Повертаємо дані ---")
        return Response(response_data)
    
# --- Кастомні види для автентифікації ---
# (Рекомендація: приберіть їх і використовуйте імпорти 
# напряму в api/urls.py, як я радив раніше)
class LoginView(RestAuthLoginView):
    pass

class LogoutView(RestAuthLogoutView):
    pass

class RegisterView(RestAuthRegisterView):
    pass