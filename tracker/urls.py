from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout', views.logout, name='logout'),
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('patient/<int:device_id>/', views.patient_details, name='patient_details'),
    path('search/', views.search_patients, name='search_patients'),
    path('patient/<int:device_id>/generate_report/', views.generate_report, name='generate_report'),
    path('edit_patient/<int:device_id>/', views.edit_patient, name='edit_patient'),
    path('patient_registration/', views.patient_registration, name='patient_registration'),
    path('view_details/', views.view_details, name='view_details'),
    path('send_report/<str:device_id>/', views.send_report, name='send_report'),
    path('register/', views.register_view, name='register'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)