from django import forms
from django.forms import formset_factory
from .models import Passenger

class PassengerEntryForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Passenger Name'})
    )
    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age'})
    )
    gender = forms.ChoiceField(
        choices=Passenger.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    berth_preference = forms.ChoiceField(
        choices=Passenger.BERTH_PREF_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class BookingContactForm(forms.Form):
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email for e-ticket delivery'})
    )
    contact_phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'})
    )

PassengerFormSet = formset_factory(PassengerEntryForm, extra=1, max_num=6)
