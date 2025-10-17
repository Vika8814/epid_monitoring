# api/admin.py
from django.contrib import admin
from .models import Institution, User, Patient, Symptom, Visit

admin.site.register(Institution)
admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Symptom)
admin.site.register(Visit)