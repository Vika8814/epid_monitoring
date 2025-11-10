# api/serializers.py
from rest_framework import serializers
from .models import Institution, User, Patient, Symptom, Visit, ChatRoom, Message
from .models import Report


from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__' # Включаємо всі поля

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'

# api/serializers.py
class PatientSerializer(serializers.ModelSerializer):
    # Додаємо поле, яке бере 'username' з об'єкта 'user'
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Patient
        # Додайте 'username' до списку полів
        fields = ['id', 'user', 'username', 'some_other_field'] 
        # (замініть 'some_other_field' на ваші реальні поля)

class VisitSerializer(serializers.ModelSerializer):
    # Поля для відображення (read-only)
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)
    patient_code = serializers.CharField(source='patient.patient_code', read_only=True)
    # Для відображення симптомів використовуємо вкладений серіалізатор
    symptoms_details = SymptomSerializer(source='symptoms', many=True, read_only=True)

    # Поля для створення/оновлення (write-only) - приймаємо ID
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), write_only=True
    )
    symptoms = serializers.PrimaryKeyRelatedField(
        queryset=Symptom.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Visit
        # Включаємо всі необхідні поля
        fields = [
            'id', 'visit_date',
            # Поля для читання
            'institution_name', 'doctor_name', 'patient_code', 'symptoms_details',
            # Поля для запису
            'patient', 'symptoms',
            # Поля, що встановлюються автоматично (read-only для API)
            'institution', 'doctor'
        ]
        read_only_fields = ['visit_date', 'institution', 'doctor']

    # Перевизначаємо метод create для обробки patient_code
    def create(self, validated_data):
        # Ми отримуємо patient ID, тому додаткова логіка не потрібна
        # patient_code_str = validated_data.pop('patient_code', None) # Якщо передавали patient_code
        # patient, created = Patient.objects.get_or_create(patient_code=patient_code_str)
        # validated_data['patient'] = patient
        return super().create(validated_data)
    

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'content', 'timestamp']
        # Змінено: додано 'sender'
        read_only_fields = ['sender', 'sender_name', 'timestamp']


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'

# Створюємо кастомний серіалізатор реєстрації
class CustomRegisterSerializer(RegisterSerializer):
    # Робимо поле email необов'язковим
    email = serializers.EmailField(required=False, allow_blank=True)

    def custom_signup(self, request, user):
        # Цей метод може бути порожнім, якщо не потрібна додаткова логіка
        # після створення користувача (наприклад, збереження профілю)
        pass

class UserDetailSerializer(serializers.ModelSerializer):
    """
    Серіалізатор для GET (отримання) та PATCH/PUT (оновлення) даних користувача.
    """
    
    # --- ДОДАЙТЕ ЦЕЙ РЯДОК ---
    # Він створює нове поле 'institution_name', 
    # беручи 'name' з пов'язаного об'єкта 'institution'.
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = User
        
        # Тепер 'institution_name' є валідним полем у цьому списку
        fields = [
            'id', 
            'username', 
            'email', 
            'image', # Ваше нове поле для аватара
            'role',  # Поле ролі
            'institution_name' # Поле з назвою закладу
        ]
        
        # Поля, які не можна редагувати (вони тільки для читання)
        # Це важливо для безпеки та для логіки нашого UI
        read_only_fields = ['role', 'institution_name']

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        # 'file' - це поле, яке ми очікуємо з фронтенду
        fields = ['id', 'user', 'file', 'uploaded_at']
        # 'user' та 'uploaded_at' будуть встановлені автоматично на бекенді
        read_only_fields = ['user', 'uploaded_at']