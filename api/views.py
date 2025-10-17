# api/views.py
from rest_framework import viewsets
from .models import Institution, Visit, Symptom
from .serializers import InstitutionSerializer, VisitSerializer, SymptomSerializer

class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint, що дозволяє переглядати заклади.
    """
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer

class VisitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint, що дозволяє переглядати візити.
    """
    queryset = Visit.objects.all().order_by('-visit_date') # Сортуємо від новіших до старіших
    serializer_class = VisitSerializer

class SymptomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint, що дозволяє переглядати симптоми.
    """
    queryset = Symptom.objects.all()
    serializer_class = SymptomSerializer


    # api/views.py (додати в кінець файлу)
from django.db.models import Count
from django.db.models.functions import TruncDay
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Visit

class StatisticsView(APIView):
    """
    API endpoint для отримання статистичних даних для дашборду.
    """
    def get(self, request, *args, **kwargs):
        # 1. Динаміка захворювань по днях (для лінійного графіка)
        disease_dynamics = (
            Visit.objects
            .annotate(day=TruncDay('visit_date'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )

        # 2. Розподіл захворювань за категоріями (для кругової діаграми)
        disease_distribution = (
            Visit.objects
            .values('symptoms__category')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        # Формуємо відповідь
        data = {
            'disease_dynamics': list(disease_dynamics),
            'disease_distribution': list(disease_distribution)
        }

        return Response(data)
    

    # api/views.py (додати в кінець файлу)
import numpy as np

class SIRModelingView(APIView):
    """
    API endpoint для SIR-моделювання.
    """
    def post(self, request, *args, **kwargs):
        # Отримуємо параметри з запиту, або використовуємо значення за замовчуванням
        N = int(request.data.get('population', 1000))  # Загальна популяція
        I0 = int(request.data.get('initial_infected', 1)) # Початкова кількість інфікованих
        R0 = int(request.data.get('initial_recovered', 0)) # Початкова кількість одужавших
        beta = float(request.data.get('beta', 0.2)) # Коефіцієнт контакту
        gamma = float(request.data.get('gamma', 0.1)) # Коефіцієнт одужання
        days = int(request.data.get('days', 160)) # Кількість днів симуляції

        S0 = N - I0 - R0

        S, I, R = [S0], [I0], [R0]

        for t in range(days - 1):
            new_infections = (beta * S[-1] * I[-1]) / N
            new_recoveries = gamma * I[-1]

            S_next = S[-1] - new_infections
            I_next = I[-1] + new_infections - new_recoveries
            R_next = R[-1] + new_recoveries

            S.append(S_next)
            I.append(I_next)
            R.append(R_next)

        # Формуємо відповідь
        results = {
            'days': list(range(days)),
            'susceptible': S,
            'infected': I,
            'recovered': R
        }

        return Response(results)