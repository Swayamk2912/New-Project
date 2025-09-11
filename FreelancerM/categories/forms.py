from django import forms
from .models import Category, Listing

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'category', 'budget', 'deadline']
