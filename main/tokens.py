from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """
    계정 활성화를 위한 토큰 생성기.
    기본 PasswordResetTokenGenerator를 재사용합니다.
    """

    pass


account_activation_token = AccountActivationTokenGenerator()

