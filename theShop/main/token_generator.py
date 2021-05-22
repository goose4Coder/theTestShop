from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user, timestamp):
        print('hash:', user.is_active)
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )


account_activation_token = TokenGenerator()


