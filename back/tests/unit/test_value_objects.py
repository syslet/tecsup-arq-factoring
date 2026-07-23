import pytest

from src.domain.exceptions.auth_exceptions import (
    InvalidCciException,
    InvalidDniException,
    InvalidRucException,
    WeakPasswordException,
)
from src.domain.value_objects.cci_account import CciAccount
from src.domain.value_objects.dni import Dni
from src.domain.value_objects.password import Password
from src.domain.value_objects.ruc import Ruc


def test_valid_dni() -> None:
    dni = Dni("12345678")
    assert dni.value == "12345678"


def test_invalid_dni() -> None:
    with pytest.raises(InvalidDniException):
        Dni("1234567")
    with pytest.raises(InvalidDniException):
        Dni("123456789")
    with pytest.raises(InvalidDniException):
        Dni("1234ABCD")


def test_valid_ruc() -> None:
    ruc = Ruc("20123456789")
    assert ruc.value == "20123456789"


def test_invalid_ruc() -> None:
    with pytest.raises(InvalidRucException):
        Ruc("11123456789")  # Invalid prefix
    with pytest.raises(InvalidRucException):
        Ruc("2012345678")  # Too short


def test_valid_password() -> None:
    pwd = Password("StrongPass123!")
    assert str(pwd) == "*****"


def test_weak_passwords() -> None:
    with pytest.raises(WeakPasswordException):
        Password("Short1!")
    with pytest.raises(WeakPasswordException):
        Password("lowercaseonly123!")
    with pytest.raises(WeakPasswordException):
        Password("UPPERCASEONLY123!")
    with pytest.raises(WeakPasswordException):
        Password("NoSpecialChar123")


def test_valid_cci() -> None:
    cci = CciAccount("00219100123456780123")
    assert cci.value == "00219100123456780123"


def test_invalid_cci() -> None:
    with pytest.raises(InvalidCciException):
        CciAccount("12345")
