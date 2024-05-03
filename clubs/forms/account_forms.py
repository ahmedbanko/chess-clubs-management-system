"""Forms to allow user to update their profile and password."""

from django import forms
from clubs.models import User
from django.core.validators import RegexValidator

class UserForm(forms.ModelForm):
    """Form to enable a user to update their profile."""

    class Meta:
        """Form options."""
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'experience_level', 'bio']
        widgets = { 'bio': forms.Textarea() }


class PasswordForm(forms.Form):
    """Form enabling users to change their password."""
    password_validators = [
        RegexValidator(
        # Password must contain one uppercase one lowercase and one number
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )
    ]
    password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(),
        validators=password_validators
    )
    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=password_validators
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Clean the data and generate messages for any errors."""
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')
