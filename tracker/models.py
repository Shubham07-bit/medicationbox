from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import os


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
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on save
    
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
        # Check if this is an update
        if self.pk:
            # Fetch the current patient object from the database
            old_photo = Patient.objects.get(pk=self.pk).photo
            if old_photo and old_photo != self.photo:
                # If there was an old photo and it's different from the new photo, delete the old one
                if os.path.isfile(old_photo.path):
                    os.remove(old_photo.path)

        # Call the parent class's save method
        super().save(*args, **kwargs)

        # Create default doses for a new patient
        if not self.pk:
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
    
    
