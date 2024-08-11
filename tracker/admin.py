from django.contrib import admin
from .models import Dose

from django.contrib import admin
from .models import Patient, Dose

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'age', 'gender', 'disease', 'photo')
    search_fields = ('name', 'device_id')

@admin.register(Dose)
class DoseAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'morning_dose', 'noon_dose', 'evening_dose', 'night_dose')
    list_filter = ('date', 'morning_dose', 'noon_dose', 'evening_dose', 'night_dose')
    search_fields = ('patient__name', 'date')

