from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer
from .forms import CustomUserCreationForm

# Home page view
class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any context data you need for the home page
        return context

# API Registration
class RegisterUserAPI(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# API Login
class LoginUserAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "token": token.key, 
                "user_id": user.id, 
                "username": user.username
            })
        return Response({"error": "Invalid credentials"}, status=400)

# Template-based Registration
class RegisterUserView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'user/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully!")
            
            # Auto-login after registration
            login(request, user)
            return redirect('home')
            
        return render(request, 'user/register.html', {'form': form})

# Template-based Login
class LoginUserView(View):
    def get(self, request):
        # If user is already authenticated, redirect to home
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'user/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {username}!")
            
            # Redirect to next parameter or home
            next_url = request.POST.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'user/login.html')

# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# Profile view
@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def dashboard_view(request):
    return render(request, 'user/dashboard.html')