from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserSession:
    """Domain entity representing an active user session."""

    id: int | None
    user_id: int
    token_jti: str
    ip_address: str | None
    user_agent: str | None
    is_revoked: bool
    created_at: datetime | None
    expires_at: datetime

    def is_valid(self) -> bool:
        """Checks if the session is active and not expired."""
        if self.is_revoked:
            return False
        if self.expires_at and datetime.now(self.expires_at.tzinfo) > self.expires_at:
            return False
        return True
