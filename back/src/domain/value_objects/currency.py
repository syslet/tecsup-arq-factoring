from enum import Enum


class Currency(str, Enum):
    """Enumeration representing supported monetary currencies in Factoring B2B."""

    PEN = "PEN"
    USD = "USD"
