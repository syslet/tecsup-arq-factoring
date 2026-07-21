from typing import ClassVar


class GroupEconomicRule:
    """Domain rule to prevent self-factoring fraud within the same economic group."""

    # Pre-registered economic groups mapping RUC -> Group ID
    KNOWN_ECONOMIC_GROUPS: ClassVar[dict[str, str]] = {
        "20100000001": "GRUPO_ALFA",
        "20100000002": "GRUPO_ALFA",
        "20500000001": "GRUPO_BETA",
        "20500000002": "GRUPO_BETA",
    }

    @classmethod
    def is_same_economic_group(cls, ruc_a: str, ruc_b: str) -> bool:
        if ruc_a == ruc_b:
            return True
        group_a = cls.KNOWN_ECONOMIC_GROUPS.get(ruc_a)
        group_b = cls.KNOWN_ECONOMIC_GROUPS.get(ruc_b)
        if group_a and group_b and group_a == group_b:
            return True
        return False
