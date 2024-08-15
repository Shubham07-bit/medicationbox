from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='profile_photos/default-avatar.png', upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class Patient(models.Model):
    # Patient details
    device_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    disease = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='patient_photos/', blank=True, null=True)  # New field for patient photo
    
    def __str__(self):
        return self.name
    
    def create_default_doses(self):
        # Create default doses for the current day
        today = timezone.now().date()
        Dose.objects.create(
            patient=self,
            date=today,
            morning_dose='not_taken',
            noon_dose='not_taken',
            evening_dose='not_taken',
            night_dose='not_taken'
        )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.create_default_doses()

class Dose(models.Model):
    # Dose details
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doses')
    date = models.DateField()
    morning_dose = models.CharField(max_length=20, choices=[('taken', 'Taken'), ('not_taken', 'Not Taken Yet'), ('missed', 'Missed')], default='not_taken')
    noon_dose = models.CharField(max_length=20, choices=[('taken', 'Taken'), ('not_taken', 'Not Taken Yet'), ('missed', 'Missed')], default='not_taken')
    evening_dose = models.CharField(max_length=20, choices=[('taken', 'Taken'), ('not_taken', 'Not Taken Yet'), ('missed', 'Missed')], default='not_taken')
    night_dose = models.CharField(max_length=20, choices=[('taken', 'Taken'), ('not_taken', 'Not Taken Yet'), ('missed', 'Missed')], default='not_taken')
    
    def __str__(self):
        return f"{self.patient.name} - {self.date}"
    
    
