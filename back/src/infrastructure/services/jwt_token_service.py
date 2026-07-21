import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from src.domain.exceptions.auth_exceptions import InvalidTokenException
from src.domain.services.token_service import ITokenService


class PyJwtTokenService(ITokenService):
    """PyJWT implementation of ITokenService."""

    def __init__(
        self,
        secret_key: str = "",
        algorithm: str = "HS256",
        expiration_minutes: int = 60 * 24,
    ) -> None:
        self._secret_key = secret_key or os.getenv("JWT_SECRET", "super-secret-key-factoring-2026")
        self._algorithm = algorithm
        self._expiration_minutes = expiration_minutes

    def create_access_token(self, user_id: int, email: str, role: str, jti: str) -> str:
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self._expiration_minutes)

        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int(expires_at.timestamp()),
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise InvalidTokenException("Token has expired.") from e
        except jwt.InvalidTokenError as e:
            raise InvalidTokenException("Invalid token signature or format.") from e
