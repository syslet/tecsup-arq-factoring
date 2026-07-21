from enum import Enum


class VerificationStatus(str, Enum):
    """Enumeration representing user/company verification lifecycle status."""

    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
