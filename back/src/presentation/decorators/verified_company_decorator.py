from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import g, jsonify

from src.domain.value_objects.verification_status import VerificationStatus
from src.presentation.decorators.auth_decorator import login_required


def require_verified_company(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator requiring both authentication and an APPROVED/VERIFIED company status."""

    @login_required
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        current_user = getattr(g, "current_user", None)
        if not current_user:
            return jsonify({"error": "Unauthorized"}), 401

        status_val = current_user.verification_status.value

        if status_val not in (VerificationStatus.APPROVED.value, "VERIFIED", "APPROVED"):
            return (
                jsonify(
                    {
                        "error": "Empresa no verificada",
                        "details": "Su empresa se encuentra en proceso de verificación (PENDING).",
                        "verification_status": status_val,
                    }
                ),
                403,
            )

        return f(*args, **kwargs)

    return decorated_function
