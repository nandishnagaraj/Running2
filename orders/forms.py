from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    timings = forms.DurationField(widget=forms.TextInput(attrs={'placeholder': 'MM:SS'}))

    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'country', 'state', 'city', 'timings']
        
