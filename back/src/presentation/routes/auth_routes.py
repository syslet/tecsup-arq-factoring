from flask import Blueprint, Response, g, jsonify, request
from pydantic import ValidationError

from src.application.use_cases.login_user import LoginCommand
from src.application.use_cases.register_user import RegisterUserCommand
from src.domain.exceptions.auth_exceptions import (
    InactiveUserException,
    InvalidCredentialsException,
    UserAlreadyExistsException,
)
from src.infrastructure.di.container import get_container
from src.presentation.decorators.auth_decorator import login_required
from src.presentation.schemas.auth_schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    UserResponseSchema,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register() -> tuple[Response, int]:
    """Registers a new user."""
    payload = request.get_json(silent=True) or {}
    try:
        data = RegisterRequestSchema(**payload)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.errors()}), 422

    try:
        container = get_container()
        command = RegisterUserCommand(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
        )
        user = container.register_user_use_case.execute(command)
        assert user.id is not None
        user_schema = UserResponseSchema(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )
        return jsonify(
            {
                "message": "User registered successfully",
                "user": user_schema.model_dump(),
            }
        ), 201
    except UserAlreadyExistsException as e:
        return jsonify({"error": str(e)}), 409


@auth_bp.route("/login", methods=["POST"])
def login() -> tuple[Response, int]:
    """Authenticates credentials and returns JWT access token."""
    payload = request.get_json(silent=True) or {}
    try:
        data = LoginRequestSchema(**payload)
    except ValidationError as err:
        return jsonify({"error": "Validation error", "details": err.errors()}), 422

    try:
        container = get_container()
        ip_address = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        command = LoginCommand(
            email=data.email,
            password=data.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        user, access_token, session = container.login_user_use_case.execute(command)

        assert user.id is not None
        user_schema = UserResponseSchema(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )

        return jsonify(
            {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_at": session.expires_at.isoformat(),
                "user": user_schema.model_dump(),
            }
        ), 200
    except (InvalidCredentialsException, InactiveUserException) as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout() -> tuple[Response, int]:
    """Revokes active user session."""
    jti = getattr(g, "current_jti", None)
    if not jti:
        return jsonify({"error": "No active session found"}), 400

    container = get_container()
    container.logout_user_use_case.execute(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def get_me() -> tuple[Response, int]:
    """Returns profile details of currently logged-in user."""
    user = getattr(g, "current_user", None)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    assert user.id is not None
    user_schema = UserResponseSchema(

        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    return jsonify({"user": user_schema.model_dump()}), 200
