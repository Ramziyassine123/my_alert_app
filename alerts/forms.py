# alerts/forms.py
from django import forms
from .models import Alert


class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['title', 'message', 'period']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Alert Title', 'required': True}),
            'message': forms.Textarea(attrs={'placeholder': 'Alert Message', 'required': True}),
            'period': forms.NumberInput(attrs={'min': 1, 'required': True}),
        }
