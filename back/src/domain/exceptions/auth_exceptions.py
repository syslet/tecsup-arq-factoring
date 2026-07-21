class DomainException(Exception):
    """Base exception for all domain errors."""

    pass


class InvalidDniException(DomainException):
    """Raised when DNI format is invalid."""

    def __init__(self, dni: str) -> None:
        super().__init__(f"Invalid DNI '{dni}'. Must be exactly 8 numeric digits.")
        self.dni = dni


class InvalidRucException(DomainException):
    """Raised when RUC format is invalid."""

    def __init__(self, ruc: str) -> None:
        super().__init__(
            f"Invalid RUC '{ruc}'. Must be 11 numeric digits starting with 10, 15, 17, or 20."
        )
        self.ruc = ruc


class WeakPasswordException(DomainException):
    """Raised when password does not fulfill domain complexity criteria."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidCciException(DomainException):
    """Raised when CCI bank account number is invalid."""

    def __init__(self, cci: str) -> None:
        super().__init__(f"Invalid CCI '{cci}'. Must be exactly 20 numeric digits.")
        self.cci = cci


class UserAlreadyExistsException(DomainException):
    """Raised when attempting to register a user with an existing identifier (email or DNI)."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f"User with identifier '{identifier}' already exists.")
        self.identifier = identifier


class CompanyAlreadyExistsException(DomainException):
    """Raised when attempting to register a company with an existing RUC."""

    def __init__(self, ruc: str) -> None:
        super().__init__(f"Company with RUC '{ruc}' already exists.")
        self.ruc = ruc


class InvalidCredentialsException(DomainException):
    """Raised when user credentials (email/DNI or password) are invalid."""

    def __init__(self) -> None:
        super().__init__("Invalid credentials.")


class InactiveUserException(DomainException):
    """Raised when an inactive user tries to authenticate or perform actions."""

    def __init__(self) -> None:
        super().__init__("User account is inactive.")


class AccountLockedException(DomainException):
    """Raised when a user account is locked due to excessive failed login attempts."""

    def __init__(
        self, message: str = "Account is locked due to excessive failed login attempts."
    ) -> None:
        super().__init__(message)


class UnverifiedAccountException(DomainException):
    """Raised when an unverified account attempts to perform restricted financial operations."""

    def __init__(
        self, message: str = "Account registration is pending legal verification."
    ) -> None:
        super().__init__(message)


class UnauthorizedException(DomainException):
    """Raised when authentication token or session is missing or invalid."""

    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(message)


class InvalidTokenException(DomainException):
    """Raised when a JWT token is expired, tampered with, or invalid."""

    def __init__(self, message: str = "Invalid or expired token.") -> None:
        super().__init__(message)
