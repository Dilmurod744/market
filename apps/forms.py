import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from apps.models import User, Order


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'password')


class UserRegistrationForm(ModelForm):
    confirm_password = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError("password mismatch")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class OrderModelForm(ModelForm):
    class Meta:
        model = Order
        fields = ('name', 'quantity', 'phone_number', 'product')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not re.match(r'^\+998\(\d{2}\) \d{3}-\d{2}-\d{2}$', phone_number):
            raise forms.ValidationError("Invalid phone number format. Please use the format +998(__) ___-__ - __")
        return phone_number

    ValidationError("Requested quantity exceeds available quantity")


class UserSettingsForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'intro']
