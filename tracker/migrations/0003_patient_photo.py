# Generated by Django 4.2.14 on 2024-08-10 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_patient_remove_dose_dose1_remove_dose_dose2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='patient_photos/'),
        ),
    ]
