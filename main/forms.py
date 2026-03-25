from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .board_password import hash_board_password
from .models import BoardPost


class BoardPostForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        label="비밀번호",
        help_text="게시글 수정/삭제 시 사용할 비밀번호를 입력하세요.",
    )

    class Meta:
        model = BoardPost
        # author_name은 클라이언트 IP 기반으로 서버에서 자동 설정
        fields = ["title", "password", "content"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        raw = self.cleaned_data["password"]
        instance.password = hash_board_password(raw)
        if commit:
            instance.save()
        return instance


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

