"""
Accounts forms
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "you@example.com",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "••••••••",
        }),
    )
    remember_me = forms.BooleanField(required=False, label=_("Remember me"))


class RegisterForm(forms.ModelForm):
    """
    Public self-registration form.
    Role is always FAN_INVESTOR — staff accounts are created by admins only.
    """
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )

    class Meta:
        model = User
        # role is intentionally excluded — always set to FAN_INVESTOR in save()
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "placeholder": _("First name")}),
            "last_name":  forms.TextInput(attrs={"class": "form-input", "placeholder": _("Last name")}),
            "email":      forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"}),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError(_("Passwords do not match."))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # Always assign Fan / Investor on public self-registration
        user.role = User.Role.FAN_INVESTOR
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    class Meta:
        model = UserProfile
        fields = [
            "avatar", "bio", "phone", "nationality", "city", "country",
            "website", "twitter", "instagram", "linkedin", "date_of_birth",
            "preferred_language", "notifications_email", "notifications_web",
        ]
        widgets = {
            "avatar":      forms.FileInput(attrs={"class": "form-input"}),
            "bio":         forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "phone":       forms.TextInput(attrs={"class": "form-input"}),
            "nationality": forms.TextInput(attrs={"class": "form-input"}),
            "city":        forms.TextInput(attrs={"class": "form-input"}),
            "country":     forms.TextInput(attrs={"class": "form-input"}),
            "website":     forms.URLInput(attrs={"class": "form-input"}),
            "twitter":     forms.TextInput(attrs={"class": "form-input", "placeholder": "@handle"}),
            "instagram":   forms.TextInput(attrs={"class": "form-input", "placeholder": "@handle"}),
            "linkedin":    forms.TextInput(attrs={"class": "form-input"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "preferred_language": forms.Select(attrs={"class": "form-select"},
                choices=[("en","English"),("nl","Nederlands"),("de","Deutsch"),
                         ("fr","Français"),("es","Español"),("it","Italiano")]),
        }


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-input", "placeholder": "you@example.com"}),
    )


class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "••••••••"}),
    )
