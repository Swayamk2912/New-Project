from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from jobs.models import Job
from users.models import User, Profile
from jobs.models import Job
from proposals.models import Proposal
from django.contrib.auth import authenticate, login, logout
from .forms import CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully!")
            return redirect('users:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            # If form is not valid, errors will be in form.errors
            # and will be displayed by the template
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.role == 'freelancer':
                return redirect('home')
            elif user.role == 'client':
                return redirect('home') 
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def home(request):
    return render(request, 'users/home.html')

User = get_user_model()

@login_required
def freelancer_list(request):
    freelancers = User.objects.filter(role='freelancer')
    return render(request, 'users/freelancer_list.html', {'freelancers': freelancers})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            # Only send one email, regardless of how many users share the email address
            # This prevents user enumeration attacks.
            associated_users = User.objects.filter(email=email)
            if associated_users.exists():
                # For simplicity, we'll just take the first user found.
                # In a real-world scenario, you might send a generic email
                # without confirming if the email exists or which user it belongs to.
                user = associated_users.first()
                subject = "Password Reset Requested"
                email_template_name = "users/password_reset_email.html"
                context = {
                    "email": user.email,
                    "domain": request.get_host(),
                    "site_name": "YourSite",
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "user": user,
                    "token": default_token_generator.make_token(user),
                    "protocol": "http",
                }
                email_body = render_to_string(email_template_name, context)
                send_mail(
                    subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(request, "Password reset email sent.")
                return redirect("users:password_reset_done")
            else:
                # Even if no user is associated, we redirect to password_reset_done
                # to avoid revealing whether an email address is registered.
                messages.info(request, "If an account with that email exists, we've sent password reset instructions.")
                return redirect("users:password_reset_done")
    else:
        form = PasswordResetForm()
    return render(request, "users/password_reset_form.html", {"form": form})

def password_reset_done(request):
    return render(request, "users/password_reset_done.html")

# ============================
# Password Reset Confirm
# ============================
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password has been reset. You can now log in.")
                return redirect("users:password_reset_complete")
        else:
            form = SetPasswordForm(user)
        return render(request, "users/password_reset_confirm.html", {"form": form})
    else:
        messages.error(request, "The password reset link is invalid or has expired.")
        return redirect("users:password_reset_request")

def password_reset_complete(request):
    return render(request, "users/password_reset_complete.html")

@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'users/profile.html', context)

@login_required
def freelancer_dashboard(request):
    if request.user.role == 'freelancer':
        proposals = Proposal.objects.filter(freelancer=request.user).order_by('-created_at')
        context = {
            'proposals': proposals,
            'is_proposals_sent_page': False # Explicitly set for the main dashboard
        }
        return render(request, 'users/freelancer_dashboard.html', context)
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')




@login_required
def proposals_sent_view(request):
    if request.user.role == 'freelancer':
        proposals = Proposal.objects.filter(freelancer=request.user).order_by('-created_at')
        context = {
            'proposals': proposals,
            'is_proposals_sent_page': True # Indicate this is the proposals sent page
        }
        return render(request, 'users/freelancer_dashboard.html', context)
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')


@login_required
def freelancer_detail(request, pk):
    freelancer = get_user_model().objects.get(pk=pk, role='freelancer')
    context = {
        'freelancer': freelancer
    }
    return render(request, 'users/freelancer_detail.html', context)

@login_required
def client_dashboard(request):
    if request.user.role != 'client':
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    client_jobs = Job.objects.filter(client=request.user).prefetch_related('proposals__freelancer__profile')

    context = {
        'client_jobs': client_jobs,
    }
    return render(request, 'users/client_dashboard.html', context)


class RegisterUserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.pk, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUserAPI(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.pk, 'email': user.email}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
