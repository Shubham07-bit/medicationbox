from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Dose, Patient, UserProfile
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.dateparse import parse_date
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .forms import UserLoginForm, UserRegistrationForm, PatientRegistrationForm,UserProfileForm, UserUpdateForm, ProfileUpdateForm, AuthenticationForm
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

@login_required(login_url='login')
def patient_dashboard(request):
    update_profile(request)
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

@login_required(login_url='login')
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('patient_dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'tracker/update_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required(login_url='login')
def patient_details(request, device_id):
    patient = get_object_or_404(Patient, device_id=device_id)
    context = {
        'patient': patient,
    }
    return render(request, 'tracker/view-details.html', context)

@login_required(login_url='login')
def search_patients(request):
    search_query = request.GET.get('query', '')
    if search_query:
        patients = Patient.objects.filter(name__icontains=search_query)
    else:
        patients = Patient.objects.none()
    
    data = list(patients.values('id', 'name', 'age', 'gender', 'disease'))
    return JsonResponse({'patients': data})

@login_required(login_url='login')
def patient_registration(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Save the new patient record to the database
            return redirect('patient_dashboard')  
    else:
        form = PatientRegistrationForm()
    return render(request, 'tracker/patient-registration.html')

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def contact(request):
    pass

@login_required(login_url='login')
def help(request):
    pass
@login_required(login_url='login')
def view_details(request):
    return render(request, 'tracker/view-details.html')

@login_required(login_url='login')
def logout(request):
    auth_logout(request)
    return redirect('login')



