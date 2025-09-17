from django import forms
from .models import Proposal

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['message', 'budget', 'timeline']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300', 'rows': 5, 'placeholder': 'Your proposal message'}),
            'budget': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300', 'placeholder': 'Your proposed budget'}),
            'timeline': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring focus:border-blue-300', 'placeholder': 'e.g., 2 weeks, 1 month'}),
        }
