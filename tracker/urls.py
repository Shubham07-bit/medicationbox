from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('home/', views.home, name='home'),
    path('weekly_report/', views.weekly_report, name='weekly_report'),  # No week_number parameter
    path('monthly_report/', views.monthly_report, name='monthly_report'),
    path('api/real_time_data/', views.real_time_data, name='real_time_data'),
    path('real_time_report/', views.real_time_data, name='real_time_report'),
    path('send_report/', views.send_report, name='send_report'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('test-pdf-render/', views.test_pdf_render, name='test_pdf_render'),
]