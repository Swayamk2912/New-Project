from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        if user.pk and not user.role:
            # User exists but has no role, redirect to role selection
            return redirect(reverse('users:select_role'))

    def get_login_redirect_url(self, request):
        if not request.user.role:
            return reverse('users:select_role')
        
        if request.user.role == 'client':
            return reverse('users:client_dashboard')
        elif request.user.role == 'freelancer':
            return reverse('users:freelancer_dashboard')
        
        return super().get_login_redirect_url(request)
