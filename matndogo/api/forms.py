from django import forms
from .models import User, Address
from django.core.exceptions import ValidationError
from .validators import phone_number_validator


class UserCreationForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=13, help_text="This field is required")
    first_name = forms.CharField(
        max_length=150, help_text="This field is required")
    last_name = forms.CharField(
        max_length=150, help_text="This field is required")

    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name"]

    def clean_phone_number(self):
        phone_no = self.cleaned_data.get("phone_number")
        if not phone_no:
            raise ValidationError("please provide phone number")
        if not phone_number_validator(phone_no):
            raise ValidationError(
                "please provide valid phone number eg +254742116141")
        return phone_no

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class BookingForm(forms.Form):
    trip_id = forms.IntegerField()
    seats_number = forms.IntegerField()


class AddressUpdateForm(forms.Form):
    zip_code = forms.CharField(max_length=50)
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(max_length=150)


class UserProfileUpdateForm(forms.Form):
    profile_image = forms.FileField(required=False)
    phone_number = forms.CharField(required=False, max_length=13)
    email = forms.EmailField(required=False)

    def clean_phone_number(self):
        phone_no = self.cleaned_data.get("phone_number")
        if phone_no and not phone_number_validator(phone_no):
            raise ValidationError(
                "please provide valid phone number eg +254742116141")
        return phone_no
