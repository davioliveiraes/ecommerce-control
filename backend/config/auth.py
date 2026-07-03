from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.core.signing import BadSignature, SignatureExpired
from ninja.security import HttpBearer

AUTH_TOKEN_SALT = "ecommerce.auth.token"


def create_auth_token(user) -> str:
    return signing.dumps({"user_id": user.pk}, salt=AUTH_TOKEN_SALT)


def get_user_from_token(token: str):
    data = signing.loads(
        token,
        salt=AUTH_TOKEN_SALT,
        max_age=settings.AUTH_TOKEN_MAX_AGE_SECONDS,
    )
    user_model = get_user_model()
    return user_model.objects.get(pk=data["user_id"], is_active=True)


class SignedBearerAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            return get_user_from_token(token)
        except (BadSignature, SignatureExpired, KeyError):
            return None
        except get_user_model().DoesNotExist:
            return None


auth = SignedBearerAuth()


def authenticate_user(identifier: str, password: str):
    """Autentica por username ou e-mail (o campo de login aceita os dois)."""
    identifier = identifier.strip()
    user = authenticate(username=identifier, password=password)
    if user is None and "@" in identifier:
        match = (
            get_user_model()
            .objects.filter(email__iexact=identifier, is_active=True)
            .first()
        )
        if match is not None:
            user = authenticate(username=match.username, password=password)
    if user is None or not user.is_active:
        return None
    return user
