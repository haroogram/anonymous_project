from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
    UserCreationForm,
)
from django.contrib.auth.models import User

from .board_password import hash_board_password
from .models import BoardComment, BoardPost


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


class BoardCommentForm(forms.ModelForm):
    class Meta:
        model = BoardComment
        fields = ["content"]
        labels = {"content": "댓글"}
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "maxlength": "2000",
                    "rows": 4,
                    "placeholder": "댓글을 입력하세요.",
                    "aria-label": "댓글",
                }
            ),
        }

    def clean_content(self):
        text = (self.cleaned_data.get("content") or "").strip()
        if not text:
            raise forms.ValidationError("내용을 입력해 주세요.")
        return text


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="아이디 또는 이메일")

    def clean(self):
        # 기본 AuthenticationForm 검증 사용
        cleaned_data = super().clean()
        return cleaned_data


class PasswordResetRequestForm(PasswordResetForm):
    email = forms.EmailField(
        required=True,
        label="이메일",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )


class PasswordResetSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="새 비밀번호",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="새 비밀번호 확인",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

