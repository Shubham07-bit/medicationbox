from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Dose, Patient
from datetime import datetime

from django.utils.dateparse import parse_date
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .forms import UserLoginForm, UserRegistrationForm, PatientRegistrationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('patient_dashboard')  # Redirect to a success page or home
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'tracker/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)
            messages.success(request, "Registration successful. You can login to your account.")
            return redirect('login')  # Redirect to a success page or home
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'tracker/register.html', {'form': form})

from django.utils import timezone
from django.db.models import Q

def patient_dashboard(request):
    search_query = request.GET.get('search', '')
    today = timezone.now().date()
    
    if search_query:
        patients = Patient.objects.filter(name__icontains=search_query)
    else:
        patients = Patient.objects.all()

    # Get today's doses
    doses_today = Dose.objects.filter(date=today)
    # Create a dictionary mapping device_id to doses
    patient_doses = {}
    for dose in doses_today:
        if dose.patient.device_id not in patient_doses:
            patient_doses[dose.patient.device_id] = []
        patient_doses[dose.patient.device_id].append(dose)

    return render(request, 'tracker/patient-dashboard.html', {
        'patients': patients,
        'patient_doses': patient_doses,
    })


def patient_details(request, device_id):
    patient = get_object_or_404(Patient, device_id=device_id)
    context = {
        'patient': patient,
    }
    return render(request, 'tracker/view-details.html', context)

def search_patients(request):
    search_query = request.GET.get('query', '')
    if search_query:
        patients = Patient.objects.filter(name__icontains=search_query)
    else:
        patients = Patient.objects.none()
    
    data = list(patients.values('id', 'name', 'age', 'gender', 'disease'))
    return JsonResponse({'patients': data})

def patient_registration(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the new patient record to the database
            return redirect('patient_dashboard')  
    else:
        form = PatientRegistrationForm()
    return render(request, 'tracker/patient-registration.html')

def generate_report(request, device_id):
    patient = get_object_or_404(Patient, device_id=device_id)
    if request.method == 'POST':
        start_date_str = request.POST.get('start-date')
        end_date_str = request.POST.get('end-date')

        if not start_date_str or not end_date_str:
            messages.error(request, 'Both start date and end date are required.')
            return redirect('patient_details', device_id=device_id)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please select valid dates.')
            return redirect('patient_details', device_id=device_id)

        request.session['start_date'] = start_date_str
        request.session['end_date'] = end_date_str

        report_data = Dose.objects.filter(patient=patient, date__range=[start_date, end_date])

        return render(request, 'tracker/view-details.html', {
            'patient': patient,
            'report_data': report_data,
            'start_date': start_date_str,
            'end_date': end_date_str,
        })

    # Handle GET request or redirection without dates
    start_date = request.session.get('start_date', '')
    end_date = request.session.get('end_date', '')
    return render(request, 'tracker/view-details.html', {'patient': patient, 'start_date': start_date, 'end_date': end_date})

def send_report(request, device_id):
    patient = get_object_or_404(Patient, device_id=device_id)
    if request.method == 'POST':
        start_date_str = request.POST.get('start-date') or request.session.get('start_date')
        end_date_str = request.POST.get('end-date') or request.session.get('end_date')

        if not start_date_str or not end_date_str:
            messages.error(request, 'Both start date and end date are required.')
            return redirect('patient_details', device_id=device_id)

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please select valid dates.')
            return redirect('patient_details', device_id=device_id)

        report_data = Dose.objects.filter(patient=patient, date__range=[start_date, end_date])

        html_content = render_to_string('tracker/report_template.html', {
            'patient': patient,
            'report_data': report_data,
            'start_date': start_date_str,
            'end_date': end_date_str,
        })

        pdf = BytesIO()
        pisa_status = pisa.CreatePDF(html_content, dest=pdf)
        pdf.seek(0)

        if pisa_status.err:
            return HttpResponse('We had some errors while generating the PDF')

        subject = f"Health Report for {patient.name}"
        email = EmailMessage(subject, 'Please find the attached report.', to=['shubhamjolapara256@gmail.com'])
        email.attach(f"Health_Report_{patient.name}_{start_date}_to_{end_date}.pdf", pdf.read(), 'application/pdf')
        email.send()

        messages.success(request, 'PDF report sent successfully.')
        return redirect('patient_details', device_id=device_id)

    return redirect('patient_details', device_id=device_id)


def contact(request):
    pass

def help(request):
    pass

def view_details(request):
    return render(request, 'tracker/view-details.html')





