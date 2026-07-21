from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import g, jsonify, request

from src.domain.exceptions.auth_exceptions import (
    DomainException,
)
from src.infrastructure.di.container import get_container


def login_required(f: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to enforce authentication on Flask routes."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization Bearer token required"}), 401

        token = auth_header.split(" ")[1]

        try:
            container = get_container()
            use_case = container.get_current_user_use_case
            current_user = use_case.execute(token)
            payload = container.token_service.decode_token(token)

            g.current_user = current_user
            g.current_jti = payload.get("jti")
            g.current_token = token
        except DomainException as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": f"Invalid token: {e}"}), 401

        return f(*args, **kwargs)

    return decorated_function
