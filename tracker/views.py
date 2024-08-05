from django.shortcuts import render, redirect
from django.utils.timezone import now
from .models import Dose
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .forms import RegistrationForm, LoginForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from datetime import datetime



def home(request):
    return render(request, 'tracker/home.html')


def weekly_report(request):
    start_date = now().date() - timedelta(days=now().date().weekday())
    end_date = start_date + timedelta(days=6)
    doses = Dose.objects.filter(date__range=[start_date, end_date])
    return render(request, 'tracker/weekly_report.html', {'doses': doses})

def monthly_report(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        year = request.POST.get('year')
    else:
        today = now().date()
        month = today.month
        year = today.year

    doses = Dose.objects.filter(date__month=month, date__year=year)
    return render(request, 'tracker/monthly_report.html', {'doses': doses, 'month': month, 'year': year})

def generate_pdf_html(doses_weekly, doses_monthly):
    html_string = render_to_string('tracker/weekly_monthly_report.html', {
        'doses_weekly': doses_weekly,
        'doses_monthly': doses_monthly,
    })

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_string.encode("UTF-8")), dest=result)
    pdf_file = result.getvalue()
    result.close()
    
    return pdf_file


def send_email(doses_weekly, doses_monthly):
    pdf = generate_pdf_html(doses_weekly, doses_monthly)
    
    email = EmailMessage(
        'Two Weeks Medication Report',
        'Please find the attached report.',
        'shubhamjolapara256@gmail.com',  # Replace with your email address
        ['shubham.jolapara@iitgn.ac.in'],  # Replace with recipient's email address
    )
    email.attach('report.pdf', pdf, 'application/pdf')
    email.send()

def send_report(request):
    try:
        end_date = now().date()
        start_date_week = end_date - timedelta(days=13)
        start_date_month = end_date - timedelta(days=30)

        doses_weekly = Dose.objects.filter(date__range=[start_date_week, end_date])
        doses_monthly = Dose.objects.filter(date__range=[start_date_month, end_date])

        if doses_weekly.exists() or doses_monthly.exists():
            send_email(doses_weekly, doses_monthly)
            return HttpResponse("Reports sent successfully!")
        else:
            return HttpResponse("No doses found for the given period.")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")
    
def test_pdf_render(request):
    end_date = now().date()
    start_date_week = end_date - timedelta(days=13)
    start_date_month = end_date - timedelta(days=30)

    doses_weekly = Dose.objects.filter(date__range=[start_date_week, end_date])
    doses_monthly = Dose.objects.filter(date__range=[start_date_month, end_date])

    return render(request, 'tracker/weekly_monthly_report.html', {
        'doses_weekly': doses_weekly,
        'doses_monthly': doses_monthly,
    })


def real_time_data(request):
    # Get month and year from request parameters
    month = request.GET.get('month')
    year = request.GET.get('year')

    today = now().date()
    
    # Calculate weekly data
    start_date_week = today - timedelta(days=today.weekday())
    end_date_week = start_date_week + timedelta(days=6)
    doses_weekly = Dose.objects.filter(date__range=[start_date_week, end_date_week]).order_by('date')
    weekly_data = list(doses_weekly.values('date', 'dose1', 'dose2', 'dose3', 'dose4'))

    # Calculate monthly data
    if month and year:
        try:
            month = int(month)
            year = int(year)
        except ValueError:
            return JsonResponse({'error': 'Invalid month or year'}, status=400)

        # Ensure month is within the valid range
        if month < 1 or month > 12:
            return JsonResponse({'error': 'Month must be between 1 and 12'}, status=400)
        
        start_date_month = datetime(year, month, 1)
        end_date_month = (datetime(year, month + 1, 1) - timedelta(days=1)) if month < 12 else (datetime(year + 1, 1, 1) - timedelta(days=1))
        doses_monthly = Dose.objects.filter(date__range=[start_date_month, end_date_month]).order_by('date')
        monthly_data = list(doses_monthly.values('date', 'dose1', 'dose2', 'dose3', 'dose4'))
    else:
        # Default to the current month if no month/year provided
        start_date_month = today.replace(day=1)
        end_date_month = (start_date_month + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        doses_monthly = Dose.objects.filter(date__range=[start_date_month, end_date_month]).order_by('date')
        monthly_data = list(doses_monthly.values('date', 'dose1', 'dose2', 'dose3', 'dose4'))

    # Return both weekly and monthly data
    return JsonResponse({'weekly': weekly_data, 'monthly': monthly_data})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('real_time_report')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to the home view
            else:
                messages.error(request, "Credentials are not correct")
        else:
            messages.error(request, "Credentials are not correct")
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('index')
