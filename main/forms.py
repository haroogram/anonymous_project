from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="이메일")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="아이디 또는 이메일")

    def clean(self):
        # 기본 AuthenticationForm 검증 사용
        cleaned_data = super().clean()
        return cleaned_data

