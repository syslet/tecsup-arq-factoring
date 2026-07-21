from enum import Enum


class UserRole(str, Enum):
    """Enumeration representing system user roles."""

    ADMIN = "ADMIN"
    CLIENT = "CLIENT"
    EXECUTIVE = "EXECUTIVE"
    GIRADOR = "GIRADOR"
    ADMINISTRADOR = "ADMINISTRADOR"
    ASESOR = "ASESOR"
