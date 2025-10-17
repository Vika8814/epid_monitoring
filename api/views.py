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