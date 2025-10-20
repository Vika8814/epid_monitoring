# api/admin.py
from django.contrib import admin
from .models import Institution, User, Patient, Symptom, Visit, ChatRoom, Message

admin.site.register(Institution)
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Symptom)
admin.site.register(Visit)
admin.site.register(ChatRoom) # <-- Переконайтесь, що цей рядок є
admin.site.register(Message)  # <-- І цей рядок теж