from django.db import models

class Dose(models.Model):
    date = models.DateField()
    dose1 = models.BooleanField(default=False)
    dose2 = models.BooleanField(default=False)
    dose3 = models.BooleanField(default=False)
    dose4 = models.BooleanField(default=False)
