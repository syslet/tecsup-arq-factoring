from abc import ABC, abstractmethod

from src.domain.entities.negotiation_history import NegotiationHistory


class INegotiationRepository(ABC):
    """Interface for rate negotiation persistence operations."""

    @abstractmethod
    def save(self, negotiation: NegotiationHistory) -> NegotiationHistory:
        """Persists a negotiation entry."""
        pass

    @abstractmethod
    def find_by_sheet_id(self, sheet_id: int) -> list[NegotiationHistory]:
        """Retrieves negotiation history for a specific sheet."""
        pass
