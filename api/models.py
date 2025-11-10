# api/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Institution(models.Model):
    INSTITUTION_TYPES = [
        ('Клініка', 'Клініка'),
        ('Лабораторія', 'Лабораторія'),
    ]
    name = models.CharField(max_length=255, verbose_name="Назва закладу")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адреса")
    type = models.CharField(max_length=20, choices=INSTITUTION_TYPES, verbose_name="Тип закладу")

    def __str__(self):
        return self.name

class User(AbstractUser):
    USER_ROLES = [
        ('Адмін', 'Адмін'),
        ('Лікар/Лаборант', 'Лікар/Лаборант'),
        ('Аналітик', 'Аналітик'),
    ]
    role = models.CharField(max_length=20, choices=USER_ROLES, verbose_name="Роль")
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Заклад")

class Patient(models.Model):
    patient_code = models.CharField(max_length=100, unique=True, verbose_name="Код пацієнта")

    def __str__(self):
        return self.patient_code

class Symptom(models.Model):
    SYMPTOM_CATEGORIES = [
        ('Грип', 'Грип'),
        ('Вітрянка', 'Вітрянка'),
        ('Ментальні труднощі', 'Ментальні труднощі'),
    ]
    name = models.CharField(max_length=255, unique=True, verbose_name="Назва симптому")
    category = models.CharField(max_length=50, choices=SYMPTOM_CATEGORIES, verbose_name="Категорія")

    def __str__(self):
        return self.name

class Visit(models.Model):
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата візиту")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, verbose_name="Пацієнт")
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_visits', verbose_name="Лікар")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, verbose_name="Заклад")
    symptoms = models.ManyToManyField(Symptom, verbose_name="Симптоми")

    def __str__(self):
        return f"Візит {self.patient.patient_code} до {self.institution.name} ({self.visit_date.strftime('%Y-%m-%d')})"
    
# api/models.py (додати в кінець файлу)

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Назва кімнати")
    participants = models.ManyToManyField(Institution, verbose_name="Учасники")

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages', verbose_name="Кімната")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Відправник")
    content = models.TextField(verbose_name="Вміст")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Час відправки")

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Від {self.sender.username} у кімнаті {self.room.name}"
    
class Report(models.Model):
    # Посилання на користувача, який завантажив звіт
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reports'
    )
    # Поле для зберігання файлу. Файли будуть у папці 'media/reports/'
    file = models.FileField(upload_to='reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Використовуємо .path, щоб отримати назву файлу
        return f'Report ({self.file.path}) by {self.user.username}'