from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User, Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    # Profile fields for freelancers
    bio = forms.CharField(widget=forms.Textarea, required=False)
    skills = forms.CharField(required=False)
    hourly_rate = forms.DecimalField(max_digits=8, decimal_places=2, required=False)
    title = forms.CharField(max_length=100, required=False)
    portfolio = forms.URLField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "role", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            if user.role == 'freelancer':
                profile, created = Profile.objects.get_or_create(user=user)
                profile.full_name = f"{user.first_name} {user.last_name}"
                profile.bio = self.cleaned_data.get('bio')
                profile.skills = self.cleaned_data.get('skills')
                profile.hourly_rate = self.cleaned_data.get('hourly_rate')
                profile.title = self.cleaned_data.get('title')
                profile.portfolio = self.cleaned_data.get('portfolio')
                # Rating is not set by the form, so it remains None or its default value.
                profile.save()
        return user
