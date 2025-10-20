# api/serializers.py
from rest_framework import serializers
from .models import Institution, User, Patient, Symptom, Visit, ChatRoom, Message

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__' # Включаємо всі поля

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'

class VisitSerializer(serializers.ModelSerializer):
    # Робимо так, щоб у відповіді були не ID, а назви
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = Visit
        fields = ['id', 'visit_date', 'institution_name', 'doctor_name', 'patient_code', 'symptoms']

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        # Вказуємо поля для читання та запису
        fields = ['id', 'room', 'sender', 'sender_name', 'content', 'timestamp']
        # Поле 'sender' потрібне тільки для запису, воно буде встановлюватись автоматично
        read_only_fields = ['sender_name', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'